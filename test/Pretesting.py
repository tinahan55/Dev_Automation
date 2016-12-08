from lib.Device import *
from lib.Configuration import *
import logging
import os
from time import gmtime, strftime


def device_check_info(logger,device,checkitem,checkcommand,checkmatch):
    title = "[%s][%s]"%(checkitem,checkcommand)
    logger.info("%s starting"%(title))
    checkresult = device.device_send_command_match(checkcommand,5,checkmatch)
    logger.info("%s check %s result :%s"%(title,checkmatch,checkresult))
    if checkresult== False:
        logger.info("%s check %s error :%s"%(title,checkmatch,device.target_response))

def Pretesting_Cellular(device):
    configlist = list()
    profile_name ="twe"
    access_name = "internet"
    dialer_index = 0
    cellular_index = 0
    dialer_carrier = "TWM"
    cellular_usb_index="usb1"


    profile = Profile("Celluar")
    configlist.extend(profile.get_cellular_profile(profile_name,access_name))
    interface = Interface("Celluar")
    configlist.extend(interface.get_dialer_interface(dialer_index,profile_name,cellular_index))
    device.device_set_configs(configlist)

    checkitem ="Pretesting_Cellular"
    checkcommandlist = ["show cellular-profile %s"%(profile_name),"show interface all","show sim-management current-status"
        ,"ping -I %s -c5 8.8.8.8"%(cellular_usb_index)]
    checkitemlist = ["Line Index : %s"%(cellular_index),"dialer %s (.*) up"%(dialer_index)
        ,"dialer %s (.*) %s (.*)"%(dialer_index,dialer_carrier),"64 bytes from 8.8.8.8: icmp_seq=5 (.*)"]
    logger.info("[%s]Starting"%(checkitem))
    for index,value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger,device,checkitem,value,checkmatch)


def Pretesting_Wifi(device):
    configlist = list()
    profile_name ="ap-profile"
    ssid_name = "auto-testing"
    wlan_index = 0
    key_type = "wpa-psk"
    wpa_version = "auto"
    wpa_key="lilee~1234"





def set_log(filename,loggername):
    logpath = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(logpath):
        os.makedirs(logpath)
    filepath = os.path.join(logpath, filename)
    print filepath
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
    logfilename = "Pretesting%s.log"%(strftime("%Y%m%d%H%M", gmtime()))
    logger = set_log(logfilename,"Pre_Testing")
    ip ="10.2.52.51"
    port = 0
    mode ="ssh"
    username = "admin"
    password ="admin"
    device =Device_Tool(ip,port,mode,username,password,"Pre_Testing")
    if device:
        device.device_get_version()
        logger.info("Device Bios Version:%s"%(device.bios_version))
        logger.info("Device recovery image:%s"%(device.boot_image))
        logger.info("Device build image:%s"%(device.build_image))
        device.device_send_command("update terminal paging disable")

        Pretesting_Cellular(device)
