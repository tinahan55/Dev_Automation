__author__ = 'ricky.wang'
import re
import httplib2

class ImageInfo(object):

    def __init__(self,host_ip="10.2.10.17",version="3.3"):
        self.hostip = host_ip
        self.version =version
        self.imagepath = ""
        self.imageno =""

    def get_image_name(self,devicetype):
        devicetype_no ="5000"
        if devicetype =="DTS":
            devicetype_no ="2000"
        elif devicetype=="LMC":
            devicetype_no ="5000"
        elif devicetype=="LMS":
            devicetype_no="2400"
        elif devicetype=="STS":
            devicetype_no="1000"
        imagename = "%s%s_u_%s_build"%(devicetype.lower(),devicetype_no,self.version)
        return imagename

    def get_image_info(self,mode,imagename,buildno):
        httpUpgrade = httplib2.Http(disable_ssl_certificate_validation=True, timeout=5)
        header = {'Content-Type': 'application/x-www-form-urlencoded'}
        urlFW = "http://%s/weekly/v%s/"%(self.hostip,self.version)
        response, content =httpUpgrade.request(urlFW, 'GET', headers=header)
        imagelist = re.findall(imagename + '([^>]+)\.img\"', str(content))
        if mode == "target":
            imagelist = re.findall(imagename+buildno + '\.img', str(content))
            self.imageno = buildno
        else:
            print sorted(imagelist)
            self.imageno =str(imagelist[-1])
        self.imagepath = urlFW + imagename +  self.imageno + ".img"
        print "[searchFW] Last build:"+ self.imagepath

    def search_image(self, mode , devicetype,buildno="1"):
        try :
            imagename = self.get_image_name(devicetype)
            print imagename
            self.get_image_info(mode,imagename,buildno)
            return True

        except Exception, e:
             print "fail exception :"+str(e)
             print "firmware name fail, please check again"
             print "new : firmware simple name =>  dts2000_u_3.0_build, lmc5000_u_3.0_build, lms2400_u_3.0_build"
             print "target : firmware simple name =>  dts2000_u_3.0_buildXX, lmc5000_u_3.0_buildXX, lms2400_u_3.0_buildXX"
             return False



if __name__ == '__main__':
    imageserver = "10.2.10.17"
    version = '3.3'
    mode = 'target'
    devicetype = 'LMS'
    deviceip = '10.2.11.58'
    deviceport = 2045
    item = list()
    item.append()
    maintainip= '10.2.11.249'

    imageinfo = ImageInfo(imageserver,version)


