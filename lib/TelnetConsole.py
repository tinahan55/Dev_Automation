__author__ = 'ricky.wang'
import telnetlib
import time
import re
import logging
from Image import  *


class Telnet_Console(object):

    def __init__(self,ipaddress,port,username='admin',password='admin',logname="telnet_test"):
        self.ipaddress = ipaddress
        self.port = port
        self.username = username
        self.password=password
        self.telnetresult = ""
        self.telnet = None
        self.IsConnect =False
        self.telnet = telnetlib.Telnet()
        self.logger = logging.getLogger('%s.telnet'%(logname))
        self.logger.info('creating the sub log for telent')


    def login(self,checkResponse="localdomain"):
        try :
            kickresult = self.kick_off_user()
            if kickresult ==True:
                time.sleep(2)
            self.telnet = telnetlib.Telnet(self.ipaddress,int(self.port), timeout=10)
            readstring = self.telnet.read_until('Welcome to Lilee Systems', timeout=10)
            if 'Welcome to Lilee Systems' not in readstring:
                self.IsConnect = False
            else:
                self.telnet.write(("\n").encode('ascii'))
                readstring = self.telnet.read_until(checkResponse, timeout=3)
                if "localdomain" not in readstring or "bash" not in readstring:
                    self.telnet.write(("\x03" + "\n").encode('ascii'))
                    readstring = self.telnet.read_until("login:", timeout=30)
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

                    elif "localdomain" in readstring or "bash" in readstring :
                        self.IsConnect= True
                    else:
                        self.IsConnect= False
                else:
                    self.IsConnect= True
        except Exception,ex :
            self.logger.error("telnet connect fail:%s"%(str(ex)))
            self.IsConnect= False

        return self.IsConnect

    def kick_off_user(self):
        self.telnet =None
        killresult = self.__kill_User("router")
        self.logger.info("[device_connect]Kill User (Router):%s"%(killresult))
        if killresult== False:
            killresult = self.__kill_User("server")
            self.logger.info("[device_connect]Kill User (server):%s"%(killresult))
        return killresult

    def __kill_User(self,mode):
        killTmp = False
        try :
            if mode == "router" :
                telnet = telnetlib.Telnet(self.ipaddress, port=23, timeout=10)
                readstring =  telnet.read_until('Password:', timeout=3)
                if len(readstring) != 0 :
                    telnet.write("lilee1234" + "\r\n")
                    readstring = telnet.read_until('Router', timeout=5)
                    if len(readstring) != 0 :
                      telnet.write("show users" + "\r\n")
                      time.sleep(1)
                      check_readResult =  telnet.read_very_eager()
                      portTmp = str(self.port).replace("20", "")+" tty "+str(self.port).replace("20", "")
                      if portTmp in check_readResult:
                          telnet.write("clear line " + str(self.port).replace("20", "") + "\r\n")
                          time.sleep(1)
                          readstring = telnet.read_until('confirm', timeout=3)
                          telnet.write("\r\n")
                          readstring =  telnet.read_until('Router', timeout=3)
                          return True
                else :
                    self.logger.error("login router fail")
                    telnet.close()
                    return False

            elif mode == "server" :
                telnet = telnetlib.Telnet(self.ipaddress, port=3000, timeout=10)
                time.sleep(1)
                readstring = telnet.read_until('->', timeout=3)
                print "telnet connect to port = " + str(self.port)
                telnet.write("disconnect " + str(self.port) + "\r\n")
                time.sleep(1)
                readstring =  self.telnet.read_until('->', timeout=3)
                if "Port not connected" in str(readstring) :
                     self.logger.info(str(readstring))
                else :
                     self.logger.info("disconnect " + self.port + " success")

                telnet.close()
                return True
            else :
                self.logger.error( "please check mode (cisco or server)")
                return False

        except :
            self.logger.error("connect to router or server fail")
            return False

    def __set_command_mode(self,mode):
        mode_result = False
        if mode == "shell":
            self.telnet.write("\n")
            readstring =self.telnet.read_until('bash', timeout=3)
            if 'bash' not in readstring:
                self.telnet.write(("diag shell\n").encode('ascii'))
                readstring = self.telnet.read_until('Password', timeout=3)
                if "Password" in readstring:
                    self.telnet.write(("Unsupported!\n").encode('ascii'))
                    readstring =self.telnet.read_until('bash', timeout=3)
                    if 'bash' in readstring:
                        mode_result =True
            else:
                mode_result = True

        elif mode == "lilee":
            self.telnet.write("\n")
            readstring =self.telnet.read_until('localdomain', timeout=3)
            if 'localdomain' not in readstring:
                self.telnet.write("%s\n"%("exit"))
                time.sleep(2)
                readstring =self.telnet.read_until('localdomain', timeout=3)
                if 'localdomain' in readstring:
                    mode_result =True
            else:
                mode_result = True

        return mode_result


    def send_command(self,command,timeout,mode,checkResponse="localdomain",logflag = True):
        try:
            if self.__set_command_mode(mode):
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

    def send_command_match(self,command,timeout,mode,result,checkResponse="localdomain"):
         try:
            if self.__set_command_mode(mode):
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



def set_log(filename,loggername):
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


if __name__ == '__main__':

  logger = set_log("Telnet.log","telnet_test")

  logger.info("telnet")


  telnetconsole =Telnet_Console('10.2.11.58',2041,"admin","admin","telnet_test")

  telnetconsole.login()

  if telnetconsole.IsConnect:
      print telnetconsole.send_command_match("show version",2,"lilee","Lilee(.*) Ltd.","localdomain")
      print telnetconsole.send_command("cat /proc/partitions",2,"shell","sda","bash")
      print telnetconsole.send_command_match("show version",2,"lilee","Lilee(.*) Ltd.","localdomain")
      print telnetconsole.send_command("cat /proc/partitions",2,"shell","sda","bash")









