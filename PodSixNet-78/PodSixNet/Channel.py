import sys, traceback
import time

from async import asynchat
from rencode import loads, dumps

class Channel(asynchat.async_chat):
    endchars = '\0---\0'
    def __init__(self, conn=None, addr=(), server=None, map=None):
        asynchat.async_chat.__init__(self, conn, map)
        self.addr = addr
        self._server = server
        self._ibuffer = ""
        self.set_terminator(self.endchars)
        self.sendqueue = []
        self.wait = 0
        self.delay = 1000
        self.dataLen = 0
        self.dataAllowedPerSecond = 100000 # 100KB per second
        self.wait2 = 0
        self.delay2 = 30000
        self.dataLen2 = 0
        self.dataAllowedPer30Second = 1000000 # 1 mega byte per 30 sec
        self.prevClock = time.clock()

    def collect_incoming_data(self, data):
        self._ibuffer += data
        self.dataLen += len(data)
        self.dataLen2 += len(data)

        curclock = time.clock()
        tick = (curclock - self.prevClock)*1000
        if self.wait + tick > self.delay:
            self.wait = 0
            if self.dataLen > self.dataAllowedPerSecond:
                self.close()
            self.dataLen = 0
        if self.wait2 + tick > self.delay2:
            self.wait2 = 0
            if self.dataLen2 > self.dataAllowedPer30Second:
                self.close()
            self.dataLen2 = 0
        self.wait += tick
        self.wait2 += tick
        self.prevClock = curclock

    
    def found_terminator(self):
        data = loads(self._ibuffer)
        self._ibuffer = ""
        
        if type(dict()) == type(data) and data.has_key('action'):
            [getattr(self, n)(data) for n in ('Network', 'Network_' + data['action']) if hasattr(self, n)]
        else:
            print "OOB data (no such Network_action):", data
    
    def Pump(self):
        [asynchat.async_chat.push(self, d) for d in self.sendqueue]
        self.sendqueue = []
    
    def Send(self, data):
        """Returns the number of bytes sent after enoding."""
        outgoing = dumps(data) + self.endchars
        self.sendqueue.append(outgoing)
        return len(outgoing)
    
    def handle_connect(self):
        if hasattr(self, "Connected"):
            self.Connected()
        else:
            print "Unhandled Connected()"
    
    def handle_error(self):
        try:
            self.close()
        except:
            pass
        if hasattr(self, "Error"):
            self.Error(sys.exc_info()[1])
        else:
            asynchat.async_chat.handle_error(self)
    
    def handle_expt(self):
        pass
    
    def handle_close(self):
        if hasattr(self, "Close"):
            self.Close()
        asynchat.async_chat.handle_close(self)

