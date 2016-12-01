import logging
from Image import  *
from TelnetConsole import *
from SSHConsole import *



class Device_Tool(object):

    def __init__(self,ipaddress,port,connecttype,username = "admin",password ="admin",logname=""):
        self.ipaddress = ipaddress
        self.port = port
        self.username = username
        self.password=password
        self.connecttype = connecttype
        self.logname = logname
        self.logger = logging.getLogger('%s.Device_Tool'%(self.logname))
        self.logger.info('creating the sub log for Device_Tool')
        self.target = self.device_connect()

    def device_connect(self):
        if self.connecttype == "telnet":
            telnet_console =Telnet_Console(self.ipaddress,self.port,self.username,self.password,self.logname)
            #kill user
            killresult = telnet_console.kill_User("router")
            self.logger.info("[device_connect]Kill User (Router):%s"%(killresult))
            if killresult== False:
                killresult = telnet_console.kill_User("server")
                self.logger.info("[device_connect]Kill User (server):%s"%(killresult))
            if killresult ==True:
                #user login
                self.logger.info('[device_connect] login start.')
                result = telnet_console.login()
                if result ==True:
                    return telnet_console
                else:
                    return None

        elif self.connecttype == "ssh":
            ssh_console = SSHConnect(self.ipaddress,self.username,self.password,self.logname)
            ssh_console.connect()
            if ssh_console.IsConnect:
                return ssh_console
            else:
                return None

    def device_send_command(self,command):
        timeout = 10
        commandresult = False
        commandresponse = ""
        if self.connecttype == "telnet":
            if self.target!=None:
                commandresult = self.target.send_command(command,timeout)
                commandresponse = self.target .telnetresult


        elif self.connecttype =="ssh":
            if self.target!=None:
                commandresult = self.target.write_command(command,timeout)
                commandresponse = self.target.sshresult
        return commandresponse

    def device_send_command_match(self,command,timeout,matchresult):
        timeout = 10
        commandresult = False
        if self.connecttype == "telnet":
            if self.target!=None:
                commandresult = self.target.send_command_match(command,timeout,matchresult)

        elif self.connecttype =="ssh":
            if self.target!=None:
                commandresult = self.target.write_command_match(command,timeout,matchresult)
        return commandresult


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

    logger = set_log("Device.log","device_test")

    telnet_device =Device_Tool("10.2.11.58",2041,"telnet","admin","admin","device_test")

    commandresponse = telnet_device.device_send_command_match("show interface all",5,"maintenance 0(.*) up")

    logger.info(commandresponse)


    ssh_device =Device_Tool("10.2.52.51",2041,"ssh","admin","admin","device_test")

    commandresponse = ssh_device.device_send_command_match("show interface all",5,"maintenance 0(.*) up")

    logger.info(commandresponse)


