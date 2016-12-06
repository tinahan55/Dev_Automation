__author__ = 'ricky.wang'
import telnetlib
import time
import re
import httplib2
import logging
import paramiko

class SSHConnect(object):

    def __init__(self,ipaddress,username="admin",password="admin",logname="SSHConnect"):
        self.ipaddress = ipaddress
        self.username = username
        self.password=password
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sshresult = ""
        self.IsConnect =False
        self.logger = logging.getLogger('%s.ssh'%(logname))
        self.logger.info('creating the sub log for SSHConnect')

    def connect(self):
        try:
            self.ssh.connect(self.ipaddress, port=22, username=self.username, password= self.password, timeout=int(10))
            self.sshresult = ""
            time.sleep(1)
            if(self.ssh):
                self.IsConnect= True
            else:
                self.IsConnect =False
            self.logger.info("connect status :%s"%(self.IsConnect))

        except Exception,ex:
            self.logger.error("[connect]ssh login fail:%s "%(str(ex)))
            self.IsConnect =False
            self.ssh.close()

    def disconnect(self):
        try:
            self.ssh.close()
            time.sleep(1)
            self.IsConnect =False
            self.logger.info("connect status :%s"%(self.IsConnect))
        except Exception,ex:
            self.logger.error("[disconnect]ssh disconnect fail:%s "%(str(ex)))
            self.IsConnect =False

    def __set_command_mode(self,remote_conn,mode):
        mode_result = False
        if mode == "shell":
            remote_conn.send("\n")
            time.sleep(2)
            response_result = remote_conn.recv(5000)
            print response_result
            if "localdomain" in response_result:
                remote_conn.send("%s\n"%("diag shell"))
                time.sleep(2)
                response_result = remote_conn.recv(5000)
                print response_result
                if "Password" in response_result:
                    remote_conn.send("%s\n"%("Unsupported!"))
                    time.sleep(2)
                    response_result = remote_conn.recv(5000)
                    if "bash" in response_result:
                        mode_result =True
            else:
                mode_result = True

        elif mode == "lilee":
            remote_conn.send("\n")
            response_result = remote_conn.recv(5000)
            if "bash" in response_result:
                remote_conn.send("%s\n"%("exit"))
                time.sleep(2)
                response_result = remote_conn.recv(5000)
                if "localdomain" in response_result:
                    mode_result =True
            else:
                mode_result = True

        return mode_result

    def write_command(self, command,timeout,mode,logflag =True):
        try:
            mode_result = True
            if(self.ssh):
                remote_conn = self.ssh.invoke_shell()
                if self.__set_command_mode(remote_conn,mode):
                    remote_conn.send("%s\n"%(command))
                    time.sleep(timeout)
                    self.sshresult = remote_conn.recv(5000)
                    if logflag == True:
                        self.logger.info(self.sshresult)
                    return True

            else:
                self.logging.info("Connection not opened.")
        except Exception,ex:
            self.logging.error("[write_command]write command fail:%s "%(str(ex)))
            self.IsConnect =False
            self.ssh.close()

    def write_command_match(self,command,timeout,mode,result):
         try:
            if(self.ssh):
                remote_conn = self.ssh.invoke_shell()
                if self.__set_command_mode(remote_conn,mode):
                    remote_conn.send((command + "\n").encode('ascii'))
                    time.sleep(timeout)
                    self.sshresult = remote_conn.recv(5000)
                    p = re.compile(result)
                    match = p.search(self.sshresult)
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


    logger = set_log("sshconsole.log","SSHConnect")

    logger.info("SSH")


    sshconnect = SSHConnect("10.2.52.51")
    sshconnect.connect()
    if(sshconnect.IsConnect):
        #sshconnect.write_command("reboot",2)
        #time.sleep(120)
        #sshconnect.connect()
        #sshconnect.write_command("show version",2,"lilee")
        sshconnect.write_command("cat /proc/partitions",2,"shell")





