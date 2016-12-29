class Profile(object):
    def __init__(self,type):
        self.type = type

    def get_cellular_profile(self,profile_name,access_name):
        commandlist = list()
        commandlist.append("create cellular-profile \"%s\""%(profile_name))
        commandlist.append("config cellular-profile \"%s\" access-point-name \"%s\""%(profile_name,access_name))
        return commandlist

    def get_wifi_profile(self,profile_name,ssid,key_type,wpa_version,wpa_key="",auth_type="",auth_eap_type=""
                         ,eap_username="",eap_key=""):
        commandlist = list()
        commandlist.append("create wifi-profile \"%s\""%(profile_name))
        commandlist.append("config wifi-profile \"%s\" ssid \"%s\""%(profile_name,ssid))
        if key_type !="":
            commandlist.append("config wifi-profile \"%s\" authentication key-management \"%s\""%(profile_name,key_type))
            commandlist.append("config wifi-profile \"%s\" authentication wpa-version \"%s\""%(profile_name,wpa_version))
            if key_type =="wpa-psk":
                commandlist.append("config wifi-profile \"%s\" authentication wpa-psk ascii \"%s\""%(profile_name,wpa_key))
            elif key_type =="wpa-eap":
                commandlist.append("config wifi-profile \"%s\" authentication %s type \"%s\""%(profile_name,auth_type,auth_eap_type))
                commandlist.append("config wifi-profile \"%s\" authentication eap-identity \"%s\""%(profile_name,eap_username))
                commandlist.append("config wifi-profile \"%s\" authentication eap-password \"%s\""%(profile_name,eap_key))

        return commandlist

class Interface(object):
    def __init__(self,type):
        self.type = type

    def get_dialer_interface(self,dialer_index,profile_name,cellular_index):
        commandlist = list()
        commandlist.append("config add interface dialer %s"%(dialer_index))
        commandlist.append("config interface dialer %s profile \"%s\""%(dialer_index,profile_name))
        commandlist.append("config interface dialer %s line cellular %s"%(dialer_index,cellular_index))
        commandlist.append("config interface dialer %s enable"%(dialer_index))
        return commandlist

    def get_wifi_interface(self,wifi_index,profile_name,wifi_mode,ip_mode,ipaddress = "192.168.11.1",netmask="255.255.255.0"):
        commandlist = list()
        commandlist.append("config add interface wlan %s %s"%(wifi_index,wifi_mode))
        commandlist.append("config interface wlan %s profile \"%s\""%(wifi_index,profile_name))
        if ip_mode =="static":
            commandlist.append("config interface wlan %s ip address %s netmask %s"%(wifi_index,ipaddress,netmask))
        elif ip_mode =="dhcp":
            commandlist.append("config interface wlan %s ip address dhcp"%(wifi_index))
        commandlist.append("config interface wlan %s enable"%(wifi_index))
        return commandlist

    def get_port_interface(self,port_index,port_type,vlan_index,vlan_tagged,port_tagged):
        commandlist = list()
        commandlist.append("config switch add vlan %s"%(vlan_index))
        if port_type == "app-engine":
            commandlist.append("config switch vlan %s add app-engine 0 port 0"%(vlan_index,port_index))
            commandlist.append("config switch vlan %s app-engine 0 port 0 egress %s"%(vlan_index,vlan_tagged))
        elif port_type =="port":
            commandlist.append("config switch vlan %s add port %s"%(vlan_index,port_index))
            commandlist.append("config switch vlan %s port %s egress %s"%(vlan_index,port_index,vlan_tagged))
            commandlist.append("config switch port %s default vlan %s"%(port_index,vlan_index))
            commandlist.append("config switch port %s egress %s"%(port_index,port_tagged))
        return commandlist


class Function(object):
    def __init__(self,type):
        self.type = type


    def get_vlan(self,vlan_index,vlan_description,ip_mode,ipaddress,netmask):
        commandlist = list()
        commandlist.append("config add interface vlan %s"%(vlan_index))
        commandlist.append("config interface vlan %s description \"%s\""%(vlan_index,vlan_description))
        if ip_mode =="static":
            commandlist.append("config interface vlan %s ip address %s netmask %s"%(vlan_index,ipaddress,netmask))
        elif ip_mode =="dhcp":
            commandlist.append("config interface vlan %s ip address dhcp"%(vlan_index))
        commandlist.append("config interface vlan %s enable"%(vlan_index))
        return commandlist


       #for ip_type = destination or source or protocol
    def get_classifier(self,index,description,ip_type, protocol_type, port_mode, port_no,ip_address):
        commandlist = list()
        commandlist.append("config add classifier %s"%(index))
        if description!="":
            commandlist.append("config classifier %s description \"%s\""%(index,description))
        if ip_type == "protocol":
            if "port" in port_mode: # for tcp and udp + dport and sport
                commandlist.append("config classifier %s match ip protocol %s %s %s"%(index, protocol_type, port_mode, port_no))
            else: # for any and icmp
                commandlist.append("config classifier %s match ip protocol %s"%(index,protocol_type))
        else:
            commandlist.append("config classifier %s match ip %s \"%s\""%(index,ip_type,ip_address))
        return commandlist


    def get_dhcp_pool(self, pool_name, pool_start_ip, pool_end_ip, netmask, default_gateway, dns_server, dns_priority, dhcp_interface, dhcp_interface_index):
        commandlist = list()
        commandlist.append("config add dhcp-pool \"%s\""%(pool_name))
        commandlist.append("config dhcp-pool \"%s\" add ip-address-range from %s to %s"%(pool_name, pool_start_ip, pool_end_ip))
        commandlist.append("config dhcp-pool \"%s\" netmask %s"%(pool_name, netmask))
        commandlist.append("config dhcp-pool \"%s\" ip default-gateway %s"%(pool_name, default_gateway))
        commandlist.append("config dhcp-pool \"%s\" ip dns-server %s priority %s"%(pool_name, dns_server, dns_priority))
        commandlist.append("config dhcp-server pool \"%s\" add interface%s %s"%(pool_name, dhcp_interface, dhcp_interface_index))
        return commandlist


    def get_nat(self, nat_type, port, interface, interface_index, classifier_index, ip, priority):
        commandlist = list()
        if nat_type == "snat":
            if classifier_index != "":
                if port != "":
                    commandlist.append("config snat out-interface %s %s classifier %s translate-to ip %s port % priority %s"%(interface, interface_index, classifier_index, ip, port, priority))
                else:
                    commandlist.append("config snat out-interface %s %s classifier %s translate-to ip %s priority %s"%(interface, interface_index, classifier_index, ip, priority))
            else:
                commandlist.append("config snat out-interface %s %s priority %s"%(interface, interface_index, priority))
        elif nat_type == "dnat":
            if classifier_index != "":
                if port != "":
                    commandlist.append("config dnat in-interface %s %s classifier %s translate-to ip %s port % priority %s"%(interface, interface_index, classifier_index, ip, port, priority))
                else:
                    commandlist.append("config dnat in-interface %s %s classifier %s translate-to ip %s priority %s"%(interface, interface_index, classifier_index, ip, priority))
            else:
                if port != "":
                    commandlist.append("config dnat in-interface %s %s translate-to ip %s port % priority %s"%(interface, interface_index, ip, port, priority))
                else:
                    commandlist.append("config dnat in-interface %s %s translate-to ip %s priority %s"%(interface, interface_index, ip, priority))
        return commandlist

















































