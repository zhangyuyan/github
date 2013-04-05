#!/usr/bin/env python

from twisted.names.dns import DNSDatagramProtocol
from twisted.names.dns import Message
from twisted.names.dns import  Query
from twisted.names.dns import Name
from twisted.names.dns import DNSProtocol
from twisted.internet.defer import Deferred
from twisted.internet import reactor
import random
import time

class DnsDatagramProtocol(DNSDatagramProtocol):
    d = ''
    def __init__(self, controller, ip = '', reactor=None, datagram = ''):
        self.controller = controller
        self.id = random.randrange(2 ** 10, 2 ** 15)
        if reactor is None:
            from twisted.internet import reactor
        self._reactor = reactor
        self.ip = ip 
        self.datagram = datagram

    def stopProtocol(self):
        self.liveMessages = {}
        self.resends = {}
        self.transport = None
        # if self.datagram:
        #     # fp = open('success','a')
        #     # fp.write(self.ip+'::'+self.datagram+'\n')
        #     self.d.callback(self.datagram)
        #     print 'success'
        #     # fp.close()
        # else:
        #     # fp = open('err','a')
        #     # fp.write(self.ip+'\n')
        #     self.d.errback('Is failure! ')
        #     print "error "
        #     # fp.close()

    def startProtocol(self):
        self.liveMessages = {}
        self.resends = {}
        
        qd = Query()
        qd.name = Name('version.bind')
        qd.type = 16
        qd.cls = 3
        qd = [qd]
    
        self.query((self.ip, 53), qd)  
        self.d ,self.controller= self.controller, None


    def datagramReceived(self, data, addr):
        self.datagram += data
        self.d.callback(data)
        self.d = None
        m = Message()
        try:
            m.fromStr(data)
        except EOFError:
            log.msg("Truncated packet (%d bytes) from %s" % (len(data), addr))
            return
        except:
            log.err(failure.Failure(), "Unexpected decoding error")
            return
        if m.id in self.liveMessages:
            d, canceller = self.liveMessages[m.id]
            del self.liveMessages[m.id]
            canceller.cancel()
            try:
                d.callback(data)
            except:    
                log.err()
        else:
            if m.id not in self.resends:
                self.controller.messageReceived(m, self, addr)  


def finish():
    reactor.callLater(4, reactor.stop)
    # print 'finish'
def get_result(result):
    print "get_result",result
def get_error(error):
    print "get_error",error
d = Deferred()
reactor.listenUDP(0, DnsDatagramProtocol(d, '192.5.5.241'))
# reactor.listenUDP(0, DnsDatagramProtocol(d, '192.168.1.4'))
d.addCallback(get_result)
d.addErrback(get_error)
# d.addCallbacks(get_result,get_error)
d.callback(finish())
# d.addBoth(finish())
reactor.run()



