__author__ = 'mandy.wu'
import telnetlib
import time
import logging

class TelnetConnect(object):

    def __init__(self, ipaddress, port=3010, username="admin", password="admin"):
        self.ipaddress = ipaddress
        self.port = port
        self.username = username
        self.password = password
        self.telnet = telnetlib.Telnet(self.ipaddress, int(self.port), timeout = int(10))
        self.telnetresult = None
        self.IsConnect = False

        #Ref: telnetlib.Telnet(Host, port=23, timeout=10)

    def connect(self, username="admin", password="admin"):
        try:
            #Ref: self.telnet.open(self.ipaddress, port=3010, username=self.username,password=self.password,timeout=int(10))
            #Ref: self.telnet.open(self.ipaddress, self.port, timeout=10)
            self.username = username
            self.password = password
            if(self.telnet):
                self.IsConnect = True
            else:
                self.IsConnect = False

        except Exception,ex:
            print "[connect]lilee telnet connect fail:%s"%(str(ex))
            self.IsConnect = False
            self.telnet.close()

    def login(self, checkResponse="localdomain"):
        try:
            readstring = self.telnet.read_until('Welcome to Lilee Systems', timeout=10)
            if len(readstring) == 0:
                self.IsConnect = False
            else:
                readstring = self.telnet.read_until(checkResponse, timeout=3)
                if "localdomain" not in readstring:
                    self.telnet.write(("\x03"+"\n").encode('ascii'))
                    readstring = self.telnet.read_until("login:", timeout=30)
                    print readstring
                    if "login:" in readstring:
                        self.telnet.write((self.username + "\r").encode('ascii'))
                        readstring = self.telnet.read_until("Password:", timeout=3)
                        if len(readstring) != 0:
                            self.telnet.write((self.password + "\r").encode('ascii'))
                            readstring = self.telnet.read_until(checkResponse, timeout=3)
                            if len(readstring) != 0:
                                self.IsConnect = True
                                print "login success by username and password"
                            else:
                                self.IsConnect = False
                        else:
                            self.IsConnect = False
                    elif "localdomain" in readstring:
                        print "login success directly"
                        self.IsConnect = True
                    else:
                        self.IsConnect = False
                else:
                    self.IsConnect = True

        except :
            print "telnet login fail"
            self.IsConnect = False



    def write_command(self, command, checkResponse="localdomain"):
        try:
            self.telnet.write((command + "\n").encode('ascii'))
            self.telnetresult = self.telnet.read_until(checkResponse, timeout=int(5))
            if len(self.telnetresult) != 0:
                return True
            else:
                return False
        except:
            print "telnet write command error"
            return False

    def check_tunnel (self, flags="UA"):
            readstring = self.telnet.read_until(flags, timeout=3)
            if (readstring) == 0:
                print "tunnel is down"
            else:
                print "tunnel is up"



def set_log(filename):
    logging.basicConfig(filename=filename, level=logging.INFO, format='%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s',)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] (%(threadName)-10s) %(message)s')
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)

if __name__ == '__main__':
    set_log("TelnetConsole_1117_check_tunnel.log")
    telnetconnect = TelnetConnect("10.2.11.4")
    telnetconnect.connect()
    if(telnetconnect.IsConnect):
        print "connect status:%s"%(telnetconnect.IsConnect)
        telnetconnect.login()
        times = 60
        for i in range(0, times):
            telnetconnect.write_command("show version")
            logging.info(telnetconnect.telnetresult)
            telnetconnect.write_command("show boot system-image")
            logging.info(telnetconnect.telnetresult)
            telnetconnect.write_command("show mobility tunnel all")
            logging.info(telnetconnect.telnetresult)
            telnetconnect.check_tunnel()
            time.sleep(10)

