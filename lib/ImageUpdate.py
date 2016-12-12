import logging
from lib.Device import *
from lib.Image import *
from time import gmtime, strftime




class ImageTool(object):
    def __init__(self,image_host_ip="10.2.10.17",image_version="3.3",logname="Image_Tool"):
        self.image_host_ip = image_host_ip
        self.image_version = image_version
        self.logname = logname
        self.logger = logging.getLogger('%s.Image'%(self.logname))

    def __set_default_config(self,device,interface,ip_mode,ipaddress="192.168.11.1",netmask="255.255.252.0"):
        defaultcommandlist = list()
        defaultcommandlist.append("config security level permissive")
        if ip_mode == "static":
            defaultcommandlist.append("config interface %s ip address %s netmask %s"%(interface,maintainip,netmask))
        elif ip_mode =="dhcp":
            defaultcommandlist.append("config interface %s ip address dhcp"%(interface))
        defaultcommandlist.append("config interface %s enable"%(interface))
        defaultcommandlist.append("save configuration")

        #set and check default config
        device.device_set_configs(defaultcommandlist)

    def __check_device_image(self,device,build_version):
        IF_Udate = True
        Check_Command = "show boot system-image"
        Check_Build = "Running: %s"%(build_version)
        result = device.device_send_command_match(Check_Command,10,Check_Build)
        self.logger.info("check_device_image Running: %s"%(result))

        if result == True:
            IF_Udate = False
        else:
            Check_Build = "Alternative image: %s"%(build_version)
            result = device.device_send_command_match(Check_Command,10,Check_Build)
            self.logger.info("check_rack_image Alternative: %s"%(result))
            if result == True:
                cmdresult = device.device_send_command("config boot system-image " + build_version)
                self.logger.info("check config boot system-image: %s"%(cmdresult))
                if cmdresult == True:
                        rebootresult = device.device_reboot()
                        self.logger.info("check rebootresult: %s"%(rebootresult))
                        if rebootresult == True:
                            self.logger.info('[Upgrade_Rack_Fw] login success to check rack running images')
                            Check_Build = "Running: %s"%(build_version)
                            result = device.device_send_command_match(Check_Command,10,Check_Build)
                            self.logger.info("check check_rack_image Running: %s"%(result))
                            if result == True:
                                IF_Udate = False
            else:
                IF_Udate = True

        return IF_Udate

    def _upgrade(self,device,pathFW,update_build_image):

        self.logger.info("[%s]udate devicet starting.."%(devicetype))
        updatecmd = "update boot system-image " + pathFW
        if "LMC" not in device.device_product_name:
            commandlist = [updatecmd,"yes"]
            resultlist = ["disk update","download"]
            result = device.device_send_multip_command_match(commandlist,10,resultlist)
            if result == True:
                self.logger.info("start to download to update image")
                time.sleep(500)

            else:
                self.logger.error("[upgrade]fail:%s",device.target_response)
        else:
            result = device.device_send_command_match(updatecmd,5,"downloaded")
            if result == True:
                   self.logger.info("start to download to update image")
                   time.sleep(500)

        IF_Udate = self._check_device_image(device,update_build_image)
        if IF_Udate ==False:
            return True
        else:
            return False

    def Upgrade_Device_Build_Image(self,device,mode,devicetype,ip_mode,maintenanceip="192.168.11.1",netmask="255.255.255.0"):

        #search firmware
        imageinfo = ImageInfo(self.image_host_ip, self.image_version)
        searchresult = imageinfo.search_image(mode,devicetype)
        update_build_image = "LileeOS_" + self.image_version +  "_build" + imageinfo.imageno
        pingcommand ="ping -c5 %s"%(self.image_host_ip)
        pingresult = "64 bytes from %s: icmp_seq=5"%(self.image_host_ip)

        if searchresult == True and (mode == "new" or mode == "target") :
            IF_Udate = self._check_device_image(device,update_build_image)
            self.logger.info('[Upgrade_Device_Build_Image] check if need to update:%s'%(IF_Udate))
            if IF_Udate ==True:
                    pingresult = device.device_send_command_match(pingcommand,2,pingresult)
                    if pingresult != True:
                        self.logger.info('[Upgrade_Device_Build_Image][ping fail]set default config')
                        self.__set_default_config(device,"maintenance 0",ip_mode)
                        pingresult = device.device_send_command_match(pingcommand,2,pingresult)
                        if pingresult!=True:
                            self.logger.info('[Upgrade_Device_Build_Image][ping fail]start reboot')
                            rebootresult = device.device_reboot()
                            self.logger.info('[Upgrade_Device_Build_Image]reboot result:%s'%(rebootresult))
                            if rebootresult == True:
                                logger.info('[Upgrade_Device_Build_Image][after rebooting]set default config')
                                self.set_default_config(device,"maintenance 0",)
                                pingresult = device.device_send_command_match(pingcommand,2,pingresult)
                                if pingresult ==True:
                                    self.logger.info("[Upgrade_Device_Build_Image]The image is the oldest one ,need to upgrade")
                                    upgraderesult = self.upgrade(device,imageinfo.imagepath,update_build_image)
                                    self.logger.info("[Upgrade_Device_Build_Image]upgrade result:%s"%(upgraderesult))
                                else:
                                    self.logger.info('[Upgrade_Device_Build_Image][after rebooting]network had fail.')


                    else:
                        self.logger.info("[Upgrade_Device_Build_Image]The image is the oldest one ,need to upgrade")
                        upgraderesult = self.upgrade(device,imageinfo.imagepath,update_build_image)
                        self.logger.info("[Upgrade_Device_Build_Image]upgrade result:%s"%(upgraderesult))

        else :
            self.logger.error( "Please choose new or target !!")


def set_log(filename,loggername):
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
    version = '3.3'
    image_host_ip ="10.2.10.17"
    device_ip ="10.2.52.51"
    device_port = 2041
    device_connect_mode ="ssh"
    login_username = "admin"
    login_password="admin"
    ip_mode = "dhcp"
    maintenanceip ="10.2.11.250"
    netmask = "255.255.252.0"
    image_mode="new"
    logfilename = "ImageUpdate%s.log"%(strftime("%Y%m%d%H%M", gmtime()))
    logger = set_log(logfilename,"Image_Tool")
    logger.info("Image update")
    imagetool = ImageTool("Image_Tool")
    device =Device_Tool(device_ip,device_port,device_connect_mode,login_username,login_password,"Image_Tool")
    device.device_get_version()
    devicetype = device.device_product_name.split("-")[0]

    imagetool.Upgrade_Device_Build_Image(device,image_mode,devicetype,ip_mode,maintenanceip,netmask)