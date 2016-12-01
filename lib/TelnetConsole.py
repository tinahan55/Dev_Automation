__author__ = 'ricky.wang'
import telnetlib
import time
import re
import httplib2
import logging
import paramiko
import logging
from Image import  *


class Telnet_Console(object):

    def __init__(self,ipaddress,port,username='admin',password='admin',logname="Telnet_Console"):
        self.ipaddress = ipaddress
        self.port = port
        self.username = username
        self.password=password
        self.telnet = telnetlib.Telnet(self.ipaddress , int(self.port), timeout=10)
        self.telnetresult = None
        self.IsConnect =False
        self.logger = logging.getLogger('%s.telnet'%(logname))
        self.logger.info('creating the sub log for telent')

    def kill_User(self,mode):
        killTmp = False
        try :
            if mode == "router" :
               try:
                   self.telnet = telnetlib.Telnet(self.ipaddress, port=23, timeout=10)
               except:
                   self.IsConnect= False
                   return False
               readstring =  self.telnet.read_until('Password:', timeout=3)
               if len(readstring) != 0 :
                  self.telnet.write("lilee1234" + "\r\n")
                  readstring = self.telnet.read_until('Router', timeout=3)
                  if len(readstring) != 0 :
                      self.IsConnect= True
                      self.telnet.write("show users" + "\r\n")
                      time.sleep(1)
                      check_readResult =  self.telnet.read_very_eager()
                      userInfo = str(check_readResult).split("\r\n")
                      for i in range(0, len(userInfo), 1) :
                           portTmp = str(self.port).replace("20", "")
                           portTmp1 = str(portTmp).replace("20", "")
                           portTmp1 = portTmp1 + " tty " + portTmp1
                           if portTmp1 in userInfo[i] :
                              self.telnet.write("clear line " + portTmp + "\r\n")
                              time.sleep(1)
                              readstring = self.telnet.read_until('confirm', timeout=3)
                              self.telnet.write("\r\n")
                              time.sleep(1)
                              readstring =  self.telnet.read_until('router', timeout=3)
                              self.logger.info("kill user success ==> " + self.ipaddress + ":" + self.port)
                              killTmp= True
                      if killTmp != True :
                           self.logger.info("No user in")
                  self.telnet.close()
                  self.IsConnect= False
                  return True


               else :
                  self.logger.error("login router fail")
                  self.telnet.close()
                  self.IsConnect= False
                  return False

            elif mode == "server" :
                self.telnet = telnetlib.Telnet(self.ipaddress, port=3000, timeout=10)
                time.sleep(1)
                readstring = self.telnet.read_until('->', timeout=3)
                print "telnet connect to port = " + str(self.port)
                self.telnet.write("disconnect " + str(self.port) + "\r\n")
                time.sleep(1)
                readstring =  self.telnet.read_until('->', timeout=3)
                if "Port not connected" in str(readstring) :
                     self.logger.info(str(readstring))
                else :
                     self.logger.info("disconnect " + self.port + " success")

                self.telnet.close()
                return True
            else :
                self.logger.error( "please check mode (cisco or server)")
                return False

        except :
            self.logger.error("connect to router or server fail")
            self.telnet.close()
            return False

    def login(self,username ="admin",password="admin",timeout =5,checkResponse="localdomain"):
        try :
            self.username=username
            self.password =password
            if self.IsConnect == False:
               self.telnet = telnetlib.Telnet(self.ipaddress , int(self.port), timeout=10)

            readstring = self.telnet.read_until('Welcome to Lilee Systems', timeout=10)
            if len(readstring) ==0:
                self.IsConnect = False
            else:
                readstring = self.telnet.read_until(checkResponse, timeout=3)
                if "localdomain" not in readstring:
                    self.telnet.write(("\x03" + "\n").encode('ascii'))
                    readstring = self.telnet.read_until("login:", timeout=30)
                    print readstring
                    if "login" in readstring:
                       self.telnet.write((self.username + "\r").encode('ascii'))
                       readstring =self.telnet.read_until('Password:', timeout=3)
                       if len(readstring)!=0:
                           self.telnet.write((self.password + "\r").encode('ascii'))
                           readstring = self.telnet.read_until(checkResponse, timeout=3)
                           if len(readstring) !=0:
                               self.IsConnect= True
                           else:
                               self.IsConnect= False
                       else:
                           self.IsConnect= False


                    elif "localdomain" in readstring:
                        print "login success"
                        self.IsConnect= True
                    else:
                        self.IsConnect= False
                else:
                    self.IsConnect= True
        except :
            self.logger.info("telnet connect fail")
            self.IsConnect= False

        return self.IsConnect

    def send_command(self,command,timeout,checkResponse="localdomain",logflag = True):
        try:
            self.telnet.write((command + "\n").encode('ascii'))
            self.telnetresult = self.telnet.read_until(checkResponse, timeout=int(timeout))
            if logflag == True:
                    self.logger.info(self.telnetresult)
            if len(self.telnetresult)!=0:
                return True
            else:
                return False
        except :
              self.logger.info("telnet command error")
              return False

    '''
    def send_commands(self, commandlist):
        try:

            for command in commandlist:
                self.telnet.write((chr(int(3))).encode('ascii'))
                self.telnet.write((command+"\n").encode('ascii'))
                self.telnet.read_until("localdomain", timeout=5)

            self.telnet.write(("show running-configuration"+"\n").encode('ascii'))
            time.sleep(2)
            readResult = self.telnet.read_very_eager()
            for command in commandlist:
                if 'save' not in command and 'update' not in command:
                    if command not in readResult:
                        self.logger.info("[command]%s not success, set again."%(command))
                        self.telnet.write((chr(int(3))).encode('ascii'))
                        self.telnet.write((command+"\n").encode('ascii'))
                        readResult = self.telnet.read_until("localdomain", timeout=5)

            return True
        except :
              return False
              self.logger.error("telnet command error")
    '''

    def send_command_match(self,command,timeout,result,checkResponse="localdomain"):
         try:

            self.telnet.write((command + "\n").encode('ascii'))
            self.telnetresult = self.telnet.read_until(checkResponse, timeout=int(timeout))
            p = re.compile(result)
            match = p.search(self.telnetresult)
            if (match == None):
                return False
            else:
                return True
         except :
                return False

    def check_images(self,type,build):
        cmdresult = self.send_command("show boot system-image", 5, "localdomain")
        if cmdresult == True:
            commandresult = str(self.telnetresult)
            print  commandresult
            print build
            romversion = type+": "+ build
            if romversion in commandresult:
                return True
            else:
                return False
        else:
            return False

    def check_rack_image(self,ipaddress,port,consolemode,versionTmp):
        IF_Udate = True
        result = self.check_images("Running",versionTmp)
        print "check_rack_image Running: %s"%(result)

        if result == True:
            IF_Udate = False
        else:
            result = self.check_images("Alternative image",versionTmp)
            print "check_rack_image Alternative: %s"%(result)
            if result == True:
                cmdresult = self.send_command("config boot system-image " + versionTmp, 5, "localdomain")
                print "check config boot system-image: %s"%(cmdresult)
                if cmdresult == True:
                    cmdresult = self.send_command("no config boot configuration", 3, "localdomain")
                    print "check no config boot configuration: %s"%(cmdresult)
                    if cmdresult ==True :
                        rebootresult = self.reboot(ipaddress, port,consolemode)
                        print "check rebootresult: %s"%(rebootresult)
                        if rebootresult == True:
                            print '[check_rack_image] login start.'
                            result = self.login()
                            if result ==True:
                                print '[Upgrade_Rack_Fw] login success to check rack running images'
                                result = self.check_images("Running",versionTmp)
                                print "check check_rack_image Running: %s"%(result)
                                if result == True:
                                    IF_Udate = False
            else:
                IF_Udate = True

        return IF_Udate

    def set_default_config(self, devicetype,maintainip,interface):
        defaultcommandlist = list()
        netmask = "255.255.252.0"
        defaultcommandlist.append("config security level permissive")
        defaultcommandlist.append("config interface %s ip address %s netmask %s"%(interface,maintainip,netmask))
        defaultcommandlist.append("config interface %s enable"%(interface))
        defaultcommandlist.append("save configuration")

        #set and check default config
        self.send_commands(defaultcommandlist)
        time.sleep(30)

    def upgrade(self, ipAddr,port,devicetype,consolemode,pathFW,versionTmp):

        print "[%s]udate devicet starting.."%(devicetype)
        self.telnet.write(("\x03" + "\n").encode('ascii'))
        updatecmd = "update boot system-image " + pathFW
        readResult = self.telnet.write((updatecmd + "\n").encode('ascii'))
        time.sleep(2)

        if "ERROR" in str(readResult) :
            print str(readResult)
            self.telnet.close()
            return False

        try :
            downloadcheck = False
            if devicetype != "LMC":
                self.telnet.read_until('disk update', timeout=20)
                self.telnet.write(("yes" + "\n").encode('ascii'))
                print "disk update check and send yes "
                checkresult = self.telnet.read_until('download', timeout=5)
                if len(checkresult)!=0:
                    print "start to download to update image"
                    downloadcheck =True

            else:
                checkresult = self.telnet.read_until('downloaded', timeout=30)
                print "lmc check result : %s"%(checkresult)
                if len(checkresult)!=0:
                    print "start to download to update image"
                    downloadcheck =True


            if downloadcheck == True:
                checkresult = self.telnet.read_until('System update complete', timeout=500)
                if len(checkresult)!=0:
                    checkresult = self.telnet.read_until('localdomain', timeout=60)
                    if len(checkresult)!=0:
                        print '[Upgrade_Rack_Fw] system update success to check rack images'
                        IF_Udate = self.check_rack_image(ipAddr,port,consolemode,versionTmp)
                        if IF_Udate ==False:
                            return True
                        else:
                            return False


        except :
            print "No print process check item! Ugrade Fail"
            return False

    def reboot(self, ipAddr, port,consolemode):
        try :
            self.telnet.write(("reboot" + "\n").encode('ascii'))
            time.sleep(3)
            response = self.telnet.read_very_eager()
            print "response : "+ response
        except Exception, e:
            print "exception :"+str(e)


        response = self.telnet.read_very_eager()
        print "[reboot ]wait for rebooting...:%s"%(response)
        checkresult = self.telnet.read_until('starting', timeout=300)
        print "[reboot ]starting for rebooting...:%s"%(checkresult)

        if len(checkresult)!=0:
           time.sleep(1)
           checkresult = self.telnet.read_until('login:', timeout=120)
           if len(checkresult)!=0:
                   print "reboot success"
                   return True
           else:
                print "reboot success"
                return False

        else:
            return False

    def Upgrade_Rack_Fw(self,mode,console,version,telnetinfo,devicetype,maintainip):

        #search firmware
        imageinfo = ImageInfo("10.2.10.17",version)
        searchresult = imageinfo.search_image(mode,devicetype)
        versionTmp = "LileeOS_" + version +  "_build" + imageinfo.imageno


        if searchresult == True and (mode == "new" or mode == "target") :
            dev_Info = telnetinfo.split(":")
            print "device info => ip :%s , port:%s ,maintainip :%s" %(dev_Info[0],dev_Info[1],maintainip)

            #kill user
            killresult = self.killUser("router")
            print "[Upgrade_Rack_Fw]Kill User (Router):%s"%(killresult)
            if killresult== False:
                killresult = self.killUser("server")
                print "[Upgrade_Rack_Fw]Kill User (server):%s"%(killresult)


            if killresult ==True:
                #user login
                print '[Upgrade_Rack_Fw] login start.'
                result = self.login()
                if result ==True:
                    print '[Upgrade_Rack_Fw] login success to check rack images'
                    IF_Udate = self.check_rack_image(dev_Info[0],dev_Info[1],console,versionTmp)
                    print '[Upgrade_Rack_Fw] check if need to update:%s'%(IF_Udate)
                    if IF_Udate ==True:
                        cmdresult = self.send_command("no config boot configuration", 3, "localdomain")
                        print '[Upgrade_Rack_Fw]no config boot configuration:%s'%(cmdresult)
                        if cmdresult == True:
                            rebootresult = self.reboot(dev_Info[0],  dev_Info[1],console)
                            print '[Upgrade_Rack_Fw]reboot result:%s'%(rebootresult)

                            if rebootresult == True:
                                print '[Upgrade_Rack_Fw] login start.'
                                result = self.login()
                                if result ==True:
                                    print '[Upgrade_Rack_Fw] login success to set default config'
                                    self.set_default_config(devicetype,maintainip)
                                    print "The image is the oldest one ,need to upgrade"
                                    upgraderesult = self.upgrade(dev_Info[0],  dev_Info[1],console, imageinfo.imagepath,devicetype,versionTmp)
                                    if upgraderesult == True:
                                        print "upgrade success."
                                    else:
                                        print "upgrade fail."
            else :
                print "fail !!"
                print "mode ERROR, please check again !!"
                print "Please choose new or target !!"



if __name__ == '__main__':

  telnetconsole =Telnet_Console('10.2.66.50',2038)
  telnetconsole.kill_User("router")


