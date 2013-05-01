
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
from twisted.python import log
import random
from twisted.internet import defer
from twisted.names.error import DNSQueryTimeoutError

class DnsDatagramProtocol(DNSDatagramProtocol):

    def __init__(self, controller, ip = '', reactor=None):
        self.controller = controller
        self.id = random.randrange(2 ** 10, 2 ** 15)
        if reactor is None:
            from twisted.internet import reactor
        self._reactor = reactor
        self.ip = ip 

    def connectionRefused(self):
        print 'connectionRefused'
        if self.controller is not None:
            d,self.controller = self.controller,None
            d.errback()

    def query(self, address, queries, timeout=10, id=None):
        print "query"
        if not self.transport:
            print 'if not self.transport:'
            try:
                self.startListening()
            except CannotListenError:
                return defer.fail()
        if id is None:
            id = self.pickID()
        else:
            self.resends[id] = 1
        def writeMessage(m):
            self.writeMessage(m, address)
        try:
            return self._query(queries, 3, id, writeMessage)
        except DNSQueryTimeoutError:
            self.controller.errback(DNSQueryTimeoutError)
        # return self._query(queries, timeout, id, writeMessage)

    def startProtocol(self):
        print 'startProtocol'
        self.liveMessages = {}
        self.resends = {}

        qd = Query()
        qd.name = Name('version.bind')
        qd.type = 16
        qd.cls = 3
        qd = [qd]
        self.query((self.ip, 53),qd)      
    def startListening(self):
        print 'startListening'
        self._reactor.listenUDP(0, self, maxPacketSize=512)

    def makeConnection(self, transport):
        print 'makeConnection'
        assert self.transport == None
        self.transport = transport
        self.doStart()

    def doStart(self):
        print 'doStart'
        print 'self.numPorts',self.numPorts
        if not self.numPorts:
            if self.noisy:
                log.msg("Starting protocol %s" % self)
            self.startProtocol()
        self.numPorts = self.numPorts + 1

    def doStop(self):
        print 'doStop'
        assert self.numPorts > 0
        self.numPorts = self.numPorts - 1
        self.transport = None
        if not self.numPorts:
            if self.noisy:
                log.msg("Stopping protocol %s" % self)
            self.stopProtocol()

    # def _query(self, queries, timeout, id, writeMessage):
    #     print '_query'
    #     m = Message(id, recDes=1)
    #     m.queries = queries

    #     try:
    #         writeMessage(m)
    #     except:
    #         return defer.fail()

    #     resultDeferred = defer.Deferred()
    #     cancelCall = self.callLater(timeout, self._clearFailed, resultDeferred, id)
    #     self.liveMessages[id] = (resultDeferred, cancelCall)
    #     print 'resultDeferred'
    #     return resultDeferred

    def datagramReceived(self, data, addr):
        print 'datagramReceived'
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
                if self.controller is not None:
                    d,self.controller = self.controller,None
                    d.callback(data)
            except:
                log.err()
        else:
            if m.id not in self.resends:
                self.controller.messageReceived(m, self, addr)

def finish():
    reactor.callLater(5, reactor.stop)

def getResult(result):
    print "&&&&getResult",result
def getError(reason):
    print "&&&&getError",reason

d = Deferred()
reactor.listenUDP(0, DnsDatagramProtocol(d,'192.5.5.24'))
d.addCallback(getResult)
d.addErrback(getError)
reactor.run()
