__author__ = 'mandy.wu'
from lib.Configuration import *
from lib.Device import *
import os
from time import gmtime, strftime
from lib.TelnetConsole import *

def device_check_info(logger, device, checkitem, checkcommand, checkmatch):
    title = "[%s][%s]" % (checkitem, checkcommand)
    logger.info("%s starting" % (title))
    checkresult = device.device_send_command_match(checkcommand, 5, checkmatch)
    logger.info("%s check %s result: %s" % (title, checkmatch, checkresult))
    if checkresult == False:
        logger.info("%s check %s error: %s" % (title, checkmatch, device.target_response))

def get_platform(device, port_index_type1,port_index_type2):
    platform = device.device_get_response("show platform type")
    print platform
    #Due to LMS's port type is different from DTS/STS, we get platform to decide port type
    if "DTS" in platform or "STS" in platform:
        port_index = port_index_type1
    else:
        port_index = port_index_type2

    return port_index


def DTS_config(device):
    configlist = list()
    #vlan
    vlan_index = 10
    vlan_description = "DTS_vlan10"
    ip_mode = "static"
    ipaddress = "192.168.10.1"
    netmask = "255.255.255.0"
    # port
    port_index_type1 = 1
    port_index_type2 = "2/1"
    port_type = "port"
    vlan_tagged = "untagged"
    port_tagged = "untagged"
    #get platform to decide port type
    port_index = get_platform(device,port_index_type1,port_index_type2)

    function_dts = Function("DTS_vlan")
    configlist.extend(function_dts.get_vlan(vlan_index, vlan_description, ip_mode, ipaddress, netmask))
    interface_dts = Interface("DTS_port")
    configlist.extend(interface_dts.get_port_interface(port_index, port_type, vlan_index, vlan_tagged, port_tagged))
    device.device_set_configs(configlist)

    checkitem = "DTS_config"
    checkcommandlist = ["show interface all", "show interface vlan %s detail" % (vlan_index)]
    checkitemlist = ["vlan %s" % (vlan_index), "IP address : %s" % (ipaddress)]
    logger.info("[%s]Starting" % (checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger, device, checkitem, value, checkmatch)

def STS_config(device):
    configlist = list()
    # vlan
    vlan_index = 20
    vlan_description = "STS_vlan10"
    ip_mode = "static"
    ipaddress = "192.168.20.1"
    netmask = "255.255.255.0"
    # port
    port_index_type1 = 2
    port_index_type2 = "2/2"
    port_type = "port"
    vlan_tagged = "untagged"
    port_tagged = "untagged"
    # get platform to decide port type
    port_index = get_platform(device, port_index_type1, port_index_type2)

    function_sts = Function("STS_vlan")
    configlist.extend(function_sts.get_vlan(vlan_index, vlan_description, ip_mode, ipaddress, netmask))
    interface_sts = Interface("STS_port")
    configlist.extend(interface_sts.get_port_interface(port_index, port_type, vlan_index, vlan_tagged, port_tagged))

    device.device_set_configs(configlist)

    checkitem = "STS_config"
    checkcommandlist = ["show interface all", "show interface vlan %s detail" % (vlan_index)]
    checkitemlist = ["vlan %s" % (vlan_index), "IP address : %s" % (ipaddress)]
    logger.info("[%s]Starting" % (checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger, device, checkitem, value, checkmatch)

def LMS_set_vlan_port(device):
    configlist = list()
    # vlan and port
    vlan_index_list = [10, 20]
    vlan_description_list = ["LMS_vlan10", "LMS_vlan20"]
    ip_mode = "static"
    ipaddress_list = ["192.168.10.254", "192.168.20.254"]
    netmask = "255.255.255.0"
    port_index_type1 = [1, 2]
    port_index_type2 = ["2/1", "2/2"]
    port_type = "port"
    vlan_tagged = "untagged"
    port_tagged = "untagged"
    # get platform to decide port type
    port_index = get_platform(device, port_index_type1, port_index_type2)

    for index, vlan_index in enumerate(vlan_index_list):
        function = Function("LMS_vlan")
        configlist.extend(function.get_vlan(vlan_index, vlan_description_list[index], ip_mode, ipaddress_list[index], netmask))
        interface = Interface("LMS_port")
        configlist.extend(interface.get_port_interface(port_index[index], port_type, vlan_index_list[index], vlan_tagged,port_tagged))

        device.device_set_configs(configlist)

        # check_config
        checkitem = "LMS_set_vlan_port"
        checkcommandlist = ["show interface all", "show interface vlan %s detail" % (vlan_index_list[index])]
        checkitemlist = ["vlan %s" % (vlan_index_list[index]), "IP address : %s" % (ipaddress_list[index])]
        logger.info("[%s]Starting" % (checkitem))
        for index, value in enumerate(checkcommandlist):
            checkmatch = checkitemlist[index]
            device_check_info(logger, device, checkitem, value, checkmatch)


def LMS_set_dialer(device):
    configlist = list()
    # profile and dialer
    profile_name = "LTE"
    access_name = "internet"
    dialer_index = 0
    cellular_index = "0/1"

    profile = Profile("Profile")
    configlist.extend(profile.get_cellular_profile(profile_name, access_name))
    interface_dialer = Interface("LMS_dialer")
    configlist.extend(interface_dialer.get_dialer_interface(dialer_index, profile_name, cellular_index))

    device.device_set_configs(configlist)

    checkitem = "LMS_set_dialer"
    checkcommandlist = ["show interface all", "show interface dialer %s detail" % (dialer_index)]
    checkitemlist = ["dialer %s" % (dialer_index), "Operational : up"]
    logger.info("[%s]Starting" % (checkitem))
    for index, value in enumerate(checkcommandlist):
        checkmatch = checkitemlist[index]
        device_check_info(logger, device, checkitem, value, checkmatch)


def LMS_set_classifier(device):
    configlist = list()
    # classifier
    index_list = [10, 20]
    description_list = ["DTS-1 to dialer", "STS-1 to maintenance network"]
    ip_type = "source"
    protocol_type = 0
    port_mode = 0
    port_no = 0
    ip_address_list = ["192.168.10.0/24", "192.168.20.0/24"]

    for index, classifier_index in enumerate(index_list):
        classifier = Function("Classifier")
        configlist.extend(classifier.get_classifier(index_list[index], description_list[index], ip_type, protocol_type, port_mode, port_no, ip_address_list[index]))

        device.device_set_configs(configlist)

        # check_config
        checkitem = "LMS_set_classifier"
        checkcommandlist = ["show classifier %s" % (index_list[index])]
        checkitemlist = ["Classifier ID : %s" % (index_list[index])]
        logger.info("[%s]Starting" % (checkitem))
        for index, value in enumerate(checkcommandlist):
            checkmatch = checkitemlist[index]
            device_check_info(logger, device, checkitem, value, checkmatch)


def LMS_set_route_table(device):
    configlist = list()
    # route table
    route_type = "table"
    route_mode = "default "
    route_ip = 0
    route_netmask = 0
    gateway_list = ["100.92.6.80", "10.2.66.1"]
    interface = 0
    metric = 0
    table_index_list = [10, 20]
    classifier_index_list = [10, 20]
    priority_list = [1, 2]

    for index, gateway in enumerate(gateway_list):
        route = Function("Route")
        configlist.extend(route.get_route(route_type, route_mode, route_ip, route_netmask, gateway_list[index], interface, metric,table_index_list[index], classifier_index_list[index], priority_list[index]))

        device.device_set_configs(configlist)

        # check_config
        checkitem = "LMS_route_table"
        checkcommandlist = ["show route table all"]
        checkitemlist = ["%s" % (table_index_list[index])]
        logger.info("[%s]Starting" % (checkitem))
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
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s -%(message)s')
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

    logfilename = "Routing%s.log"%((strftime("%Y%m%d%H%M", gmtime())))
    logger = set_log(logfilename, "Routing_test")

    #connectType = "telnetConsole"
    #if connectType == "telnetConsole":

    #We have 1 server and 2 clients
    #server --> do routing work
    #client1 --> public route testing
    #client2 --> private route testing

    telnet_ip = "10.2.66.50"
    DTS_port = 2035
    STS_port = 2040
    LMS_port = 2038
    public_ping_ip = "8.8.8.8"
    private_ping_ip = "10.2.8.1"


    # set_up_device_config
    port_list = [DTS_port, STS_port, LMS_port]
    for index, port in enumerate(port_list):
        device = Device_Tool(telnet_ip, port_list[index], "telnet", "admin", "admin", "Routing_test")
        if device:
            if port == DTS_port:
                print "DTS connected"
                DTS_config(device)
            elif port == STS_port:
                print "STS connected"
                STS_config(device)
            elif port == LMS_port:
                print "LMS connected"
                LMS_set_vlan_port(device)
                #LMS_set_dialer(device)
                #LMS_set_classifier(device)
                #LMS_set_route_table(device)



    #routing_test
    telnet_port_list = [DTS_port, LMS_port, STS_port, LMS_port]
    command_list = ["ping %s"%(public_ping_ip), "tcpdump -i usb1 icmp" ,"ping %s"%(private_ping_ip) ,"tcpdump -i eth0 icmp"]
    print "Routing test starting"
    for index, port in enumerate(telnet_port_list):
        TelnetConsole = Telnet_Console(telnet_ip, telnet_port_list[index],"admin", "admin", "Routing_test")
        TelnetConsole.login()
        if port == DTS_port or port == STS_port:
            TelnetConsole.send_command("no config interface maintenance 0 enable", 5, "lilee", checkResponse="localdomain",logflag=True)
            TelnetConsole.send_command(command_list[index], 5, "lilee", checkResponse="localdomain", logflag=True)
        else:
            TelnetConsole.send_command(command_list[index], 5, "shell", checkResponse="bash-4.2#", logflag=True)
            time.sleep(1)
            if "%s: ICMP echo request"%(public_ping_ip) in TelnetConsole.telnetresult:
                print "public routing test successful"
            elif "%s: ICMP echo request"%(private_ping_ip) in TelnetConsole.telnetresult:
                print "private routing test successful"
            else:
                print "routing test fail"
            TelnetConsole.telnet.write(("\x03").encode('ascii'))

    #stop ping and tcpdump --> to be revised
    for index, port in enumerate(telnet_port_list):
        TelnetConsole = Telnet_Console(telnet_ip, telnet_port_list[index], "admin", "admin", "Routing_test")
        TelnetConsole.login()
        TelnetConsole.telnet.write(("\x03").encode('ascii'))





