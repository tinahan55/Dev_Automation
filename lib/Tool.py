import platform
import os
import logging


class Network(object):
    def __init__(self,logname=""):
        self.logname = logname
        self.logger = logging.getLogger('%s.Network_Tool'%(self.logname))
        self.logger.info('creating the sub log for Network_Tool')

    def Host_Ping(self,hostname,times):
        checkstring ='Reply from %s'%(hostname)
        if platform.system() == "Windows":
            response = os.system("ping %s -n %s"%(hostname,times))
        else:
            response = os.system("ping -c%s %s "%(times,hostname))
        isUpBool = False
        if response ==0:
            isUpBool = True
        return isUpBool