from lib.Device import *
from lib.Configuration_add_dhcp import *
import logging
import os
from time import gmtime, strftime

class NAT(object):
    def __init__(self, type):
        self.type = type

    def snat(self, interface, interface_index, priority):
        commandlist = list()
        commandlist.append("config snat out-interface %s %s priority %s"%(interface, interface_index, priority))
        return commandlist

    def dnat(self, classifier_index, description, protocol_type, dport, in_interface, interface_index, ip, port, priority):
        commandlist = list()
        commandlist.append("config add classifier %s"%(classifier_index))
        commandlist.append("config classifier %s description \"%s\""%(classifier_index, description))
        if protocol_type == "tcp" | "udp":
            commandlist.append("config classifier %s match ip protocol %s dport %s"%(classifier_index, protocol_type, dport))
        else:
            commandlist.append("config classifier %s match ip protocol %s"%(classifier_index, protocol_type))
        commandlist.append("config dnat in-interface %s %s classifier %s translate-to ip %s port %s priority %s"%(in_interface, interface_index, classifier_index, ip, port, priority))
        return commandlist


def set_log(filename, loggername):
    logpath = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    filepath = os.path.join(logpath, filename)
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler(filepath)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger


if __name__ == '__main__':
    logfilename = "NAT%s.log"%(strftime("%Y%m%d%H%M", gmtime()))
    logger = set_log(logfilename, "NAT_testing")
    ip = "10.2.53.153"
    port = "2222"
    mode = "ssh"
    username = "admin"
    password = "admin"
    app_engine_device = Device_Tool(ip, port, mode, username, password, "NAT")
    if app_engine_device:
        app_engine_device.device_get_version()
        logger.info("Device Bios Version: %s"%(app_engine_device.bios_version))
        logger.info("Lilee OS Version (build image): %s"%(app_engine_device.build_image))
        logger.info("Recovery Image Version: %s"%(app_engine_device.boot_image))


