#
# http://blackharmony.pl/
# 2015-11-19 areq
#
from Components.Converter.Converter import Converter
from Components.Element import cached
from socket import gethostbyname
from time import time

class BlackHarmonyVersionConverter(Converter, object):
    VERSION = 33
    def __init__(self, arg):
        Converter.__init__(self, arg)
        self.toupdate = False
        self.nextt = 0

    @cached
    def getBoolean(self):
        t = time()
        v = 0
        if self.nextt < t:
            self.nextt = t + (60 * 10)
            try:
                i1, i2, i3, i4 = [ int(i) for i in gethostbyname('version.blackharmony.pl').split('.') ]
                if i1 == 1:
                    v = i3 * 256 + i4
                    self.nextt = t + 14400   # every 4h
            except:
                pass
            self.toupdate =  self.VERSION < v

        return self.toupdate

    boolean = property(getBoolean)