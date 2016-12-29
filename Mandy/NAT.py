from lib.Device import *
from lib.Configuration import *
import logging
import os
from time import gmtime, strftime



#def NAT_port_setup(include port and app-engine)
#def dhcp_setup
#snat
#dnat


def device_check_info(logger, device, checkitem, checkcommand, checkmatch):
    title = "[%s][%s]"%(checkitem, checkcommand)
    logger.info("%s starting"%(title))
    checkresult = device.device_send_command_match(checkcommand, 5, checkmatch)
    logger.info("%s check %s result : %s"%(title, checkmatch, checkresult))
    if checkresult == False:
        logger.info("%s check %s error : %s"%(title, checkmatch, device.target_response))


def NAT_port_setup(device):
    #port
    configlist = list()
    port_type = "port"
    vlan_index = 100
    port_index = 1
    vlan_tagged = "untagged"
    port_tagged = "untagged"

    #vlan
    ip_mode = "static"
    ipaddress = "10.1.4.254"
    netmask = "255.255.255.0"
    vlan_description = "NAT  test"

    interface = Interface("Port")
    configlist.extend(interface.get_port_interface(port_index,port_type,vlan_index,vlan_tagged,port_tagged))

    #app-engine
    #port_type = "app-engine"
    #interface = Interface("app-engine")
    #configlist.extend(interface.get_port_interface(port_type))

    function = Function("vlan")
    configlist.extend(function.get_vlan(vlan_index, vlan_description, ip_mode, ipaddress, netmask))

    device.device_set_configs(configlist)

    #verify command
    checkitem = "NAT_port_setup"
    checkcommandlist = ["show interface all", "show interface vlan %s detail"%(vlan_index), "show app-engine 0 info"]

    checkitemlist = ["vlan %s"%(vlan_index), "Operational : up | MTU : 1500", "Operational : Running"]

    logger.info("[%s]Starting"%(checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger,device,checkitem,value,checkmatch)


def NAT_dhcp(device):
    configlist = list()
    pool_name = "test-dhcp"
    pool_start_ip = "10.1.4.153"
    pool_end_ip = "10.1.4.153"
    netmask = "255.255.255.0"
    default_gateway = "10.1.4.254"
    dns_server = "168.95.1.1"
    dns_priority = 1
    dhcp_interface = "vlan"
    dhcp_interface_index = 100

    function = Function("dhcp")
    configlist.extend(function.get_dhcp_pool(pool_name, pool_start_ip, pool_end_ip, netmask, default_gateway, dns_server, dns_priority, dhcp_interface, dhcp_interface_index))

    device.device_set_configs(configlist)

    #add verify command
    checkitem = "NAT_dhcp"
    checkcommandlist = ["show dhcp-server lease"]

    checkitemlist = ["%s"%(pool_start_ip)]

    logger.info("[%s]Starting"%(checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger, device, checkitem, value, checkmatch)


def NAT_classifier(device):
    configlist = list()
    index = 100
    description = "automatically added for port forwarding"
    ip_type = "protocol"
    protocol_type = "tcp"
    port_mode = "dport"
    port_no = 2222
    ip_address = "10.1.4.226"

    function = Function("classifier")
    configlist.extend(function.get_classifier(index,description,ip_type, protocol_type, port_mode, port_no,ip_address))

    device.device_set_configs(configlist)

    #add verify command
    checkitem = "NAT_classifier"
    checkcommandlist = ["show classifier %s(.*)"%(index)]

    checkitemlist = ["classifier %s up"%(index)]

    logger.info("[%s]Starting"%(checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger, device, checkitem, value, checkmatch)


def NAT(device):
    configlist = list()
    nat_type = "dnat"
    port = 22
    interface = "maintenance"
    interface_index = 0
    classifier_index = 100
    ip = "10.1.4.153"
    priority = 1

    function = Function("NAT")
    configlist.extend(function.get_nat(nat_type, port, interface, interface_index, classifier_index, ip, priority))

    device.device_set_configs(configlist)

    #add verify command
    checkitem = "NAT"
    checkcommandlist = ["show %s(.*)"%(nat_type)]

    checkitemlist = ["%s up"%(nat_type)]

    logger.info("[%s]Starting"%(checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger, device, checkitem, value, checkmatch)



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


#main( connect -> initial setup -> catch config -> compare -> append config -> show and verify)
if __name__ == '__main__':
    logfilename = "NAT%s.log"%(strftime("%Y%m%d%H%M", gmtime()))
    logger = set_log(logfilename, "NAT_testing")
    ip = "10.2.59.160"
    port = 0
    mode = "ssh"
    username = "admin"
    password = "admin"
    device = Device_Tool(ip, port, mode, username, password, "NAT")
    if device:
        device.device_get_version()
        logger.info("Device Bios Version: %s"%(device.bios_version))
        logger.info("Lilee OS Version (build image): %s"%(device.build_image))
        logger.info("Recovery Image Version: %s"%(device.boot_image))

        NAT_port_setup(device)
        #NAT_dhcp(device)
        #NAT_classifier
        #NAT(device)

        #add "save configuration" command
