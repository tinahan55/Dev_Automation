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
        self.sshresult = None
        self.IsConnect =False
        self.logger = logging.getLogger('%s.ssh'%(logname))
        self.logger.info('creating the sub log for SSHConnect')

    def connect(self):
        try:
            self.ssh.connect(self.ipaddress, port=22, username=self.username, password= self.password, timeout=int(10))
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

    def write_command(self, command,timeout,logflag =True):
        try:
            if(self.ssh):
                remote_conn = self.ssh.invoke_shell()
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

    def write_command_match(self,command,timeout,result):
         try:
            if(self.ssh):
                remote_conn = self.ssh.invoke_shell()
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



if __name__ == '__main__':
    sshconnect = SSHConnect("10.2.52.56")
    sshconnect.connect()
    if(sshconnect.IsConnect):
        times = 200000
        for k in range(0, times):
            sshconnect.write_command("debug line cellular 0 atcmd \"AT!GSTATUS?\"")
            sshconnect.write_command("debug line cellular 1 atcmd \"AT!GSTATUS?\"")
            sshconnect.write_command("show gps detail")
            time.sleep(10)

