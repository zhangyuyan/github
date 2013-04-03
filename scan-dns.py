
from twisted.names.dns import DNSDatagramProtocol
from twisted.names.dns import Message
from twisted.names.dns import  Query
from twisted.names.dns import Name
from twisted.names.dns import DNSProtocol
import struct
from twisted.names.client import DNSClientFactory
from twisted.internet.defer import Deferred
from twisted.internet import reactor
import os
from twisted.names.client import AXFRController

class DnsDatagramProtocol(DNSDatagramProtocol):

    def stopProtocol(self):
        print 'stopProtocol'
        self.liveMessages = {}
        self.resends = {}
        self.transport = None

    def startProtocol(self):
        print 'startProtocol'
        self.liveMessages = {}
        self.resends = {}

        qd = Query()
        qd.name = Name('version.bind')
        qd.type = 16
        qd.cls = 3
        qd = [qd]
        self.query(('192.5.5.241',53),qd)      


    def datagramReceived(self, data, addr):
        print 'datagramReceived'
        print data
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
                d.callback(m)
            except:
                log.err()
        else:
            if m.id not in self.resends:
                self.controller.messageReceived(m, self, addr)


d = Deferred()
reactor.listenUDP(0, DnsDatagramProtocol(d))
reactor.run()
