class Profile(object):
    def __init__(self,type):
        self.type = type

    def get_cellular_profile(self,profile_name,access_name):
        commandlist = list()
        commandlist.append("create cellular-profile \"%s\""%(profile_name))
        commandlist.append("config cellular-profile \"%s\" access-point-name \"%s\""%(profile_name,access_name))
        return commandlist

    def get_wifi_profile(self,profile_name,ssid,key_type,wpa_version,wpa_key):
        commandlist = list()
        commandlist.append("create wifi-profile \"%s\""%(profile_name))
        commandlist.append("config wifi-profile \"%s\" ssid \"%s\""%(profile_name,ssid))
        commandlist.append("config wifi-profile \"%s\" authentication key-management \"%s\""%(profile_name,key_type))
        commandlist.append("config wifi-profile \"%s\" authentication key-management wpa-version \"%s\""%(profile_name,wpa_version))
        commandlist.append("config wifi-profile \"%s\" authentication wpa-psk ascii \"%s\""%(profile_name,wpa_key))
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
        elif ip_mode =="dhcp'":
            commandlist.append("config interface wlan %s ip address dhcp"%(wifi_index))
        commandlist.append("config interface wlan %s enable"%(wifi_index))
        return commandlist







