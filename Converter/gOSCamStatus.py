#author COoLoSER

#Thanks to Crash for his contribution in skin and graphics.

from xml.dom import minidom
import socket
import urllib2, base64
from urllib2 import URLError
import re
import time

#enigma
from Components.Converter.Converter import Converter
from enigma import eTimer
from Components.Element import cached

class gOSCamStatus(Converter, object):
#class gOSCamStatus:
    SERVERS = 1
    CLIENTS = 2

    __url = "http://192.168.4.2:8083/oscamapi.html?part=status"
    __username = "admin"
    __password = "solo4k"
    __updatePeriodInSeconds = 10

    itemsP = []
    itemsC = []

    count=0
    lastUpdateTime=0

#DynamicTimer = None
# initialize object
    def __init__(self, type):
        Converter.__init__(self, type)
        gOSCamStatus.count=gOSCamStatus.count+1
    self.running = 0
    if type == "Servers":
        self.type = self.SERVERS
    elif type == "Clients":
        self.type = self.CLIENTS
#       if gOSCamStatus.DynamicTimer is None:
#           gOSCamStatus.DynamicTimer = eTimer()
#           gOSCamStatus.DynamicTimer.callback.append(self.getData)
#           self.getData();

    def doSuspend(self, suspended):
        if suspended == 0:
            self.running = 1
        else:
            self.running = 0

    def clearData(self):
        print "init=%d BYE BYE!!!" % (gOSCamStatus.count)
        gOSCamStatus.itemsP = None
        gOSCamStatus.itemsC = None
#       gOSCamStatus.DynamicTimer = None

    # get text value of xml node
    def __getText(self, node):
        rc = ""
        for tmpNode in node.childNodes:
            if tmpNode.nodeType == tmpNode.TEXT_NODE:
                rc = rc + tmpNode.data
            elif tmpNode.nodeType == tmpNode.CDATA_SECTION_NODE:
                rc = rc + tmpNode.data
        return rc

    def getData(self):
        if self.running == 0:
            return
        currentTime = time.time()
        print "init=%d currentTime %d , lastTime %d" % (gOSCamStatus.count, currentTime, gOSCamStatus.lastUpdateTime)
        if (currentTime-gOSCamStatus.lastUpdateTime)<gOSCamStatus.__updatePeriodInSeconds:
            return
        
        gOSCamStatus.lastUpdateTime = currentTime
        print "init=%d downloading from %s" % (gOSCamStatus.count, gOSCamStatus.__url)
        #dowload file
        socket.setdefaulttimeout(5)
        self.error=None
        try:
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, gOSCamStatus.__url, gOSCamStatus.__username, gOSCamStatus.__password)
            handler = urllib2.HTTPDigestAuthHandler(password_mgr)
            opener = urllib2.build_opener(handler)
            urllib2.install_opener(opener)
            rssResponse=urllib2.urlopen(gOSCamStatus.__url)
            rssXml=rssResponse.read()
        except URLError, e:
            self.error=str(e)
            print "Network problem: "+self.error
            gOSCamStatus.itemsP = None
            gOSCamStatus.itemsC = None
            return

        try:
            #check for not well-formed xml
            rssXml=rssXml.replace(" & ", " &amp; ")
            #print rssXml
            #open xml file
            #DOMTree = minidom.parse("/mnt/hdd/develop/today")
            DOMTree = minidom.parseString(rssXml)
            cNodes = DOMTree.childNodes
            #/oscam/status
            gOSCamStatus.itemsP = []
            gOSCamStatus.itemsC = []
            self.status = cNodes[0].getElementsByTagName("status")[0]
            for client in self.status.getElementsByTagName("client"):
                clientType = client.getAttribute("type");
                #print "type="+clientType
                if clientType=='p':
#                   print "Provider"
                    name=client.getAttribute("name");
                    protocol=client.getAttribute("protocol");
                    connection=client.getElementsByTagName("connection")[0]
                    ip=connection.getAttribute("ip");
                    connectionStatus=self.__getText(connection)
                    gOSCamStatus.itemsP.append([name, protocol, ip, connectionStatus])
                elif clientType=='c':
#                   print "Client"
                    name=client.getAttribute("name");
                    protocol=client.getAttribute("protocol");
                    connection=client.getElementsByTagName("connection")[0]
                    ip=connection.getAttribute("ip");
                    request=client.getElementsByTagName("request")[0]
                    ecmTime=request.getAttribute("ecmtime");
                    answered=request.getAttribute("answered");
                    channel=self.__getText(request)
                    gOSCamStatus.itemsC.append([name, protocol, ip, ecmTime, answered, channel])
            print "Providers:\n", gOSCamStatus.itemsP
            print "\n"
            print "Clients:\n", gOSCamStatus.itemsC
#           gOSCamStatus.DynamicTimer.start(5000, True)
#           Converter.changed(self, (self.CHANGED_POLL,))

        except Exception, e:
            self.error=str(e)
            gOSCamStatus.itemsP = None
            gOSCamStatus.itemsC = None
            print "Parsing problem: "+self.error

    @cached
    def getText(self):
        self.getData();
        result = ""
        if (self.type == self.SERVERS):
            print "Servers", gOSCamStatus.itemsP
            if not (gOSCamStatus.itemsP is None):
                for item in gOSCamStatus.itemsP:
                    result += "%s IP %s  %s\n" % (item[0].ljust(7), item[2].ljust(15), item[3])
                
        elif (self.type == self.CLIENTS):
            print "Clients", gOSCamStatus.itemsC
            if not (gOSCamStatus.itemsC is None):
                for item in gOSCamStatus.itemsC:
                    #result += "%s IP %s  %s %s\n" % (item[0].ljust(11), item[2].ljust(14), item[5], item[3])   
                    result += "%s %s IP %s %s\n" % (item[0].ljust(12), item[1].ljust(24), item[2].ljust(16), item[4])
        print result
        result2 = str(result)
        print type(result), type(result2)
        return result2

    text = property(getText)
