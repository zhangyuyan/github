#!/usr/bin/env python

from twisted.names.dns import DNSDatagramProtocol
from twisted.names.dns import DNSProtocol
from twisted.names.dns import Message
from twisted.names.dns import  Query
from twisted.names.dns import Name
from twisted.names.dns import DNSProtocol
from twisted.names.client import DNSClientFactory
from twisted.internet.defer import Deferred
from twisted.internet import reactor
import random
import time
from twisted.names.dns import  Query
import struct
import traceback
from twisted.internet import task
from twisted.internet import defer
import StringIO
from twisted.python import log

class DnsProtocol(DNSProtocol):
    def connectionMade(self):
        self.liveMessages = {}

        qd = Query()
        qd.name = Name('version.bind')
        qd.type = 16
        qd.cls = 3
        qd = [qd]    
        self.query(qd)  

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        self.buffer += data

        while self.buffer:
            if self.length is None and len(self.buffer) >= 2:
                self.length = struct.unpack('!H', self.buffer[:2])[0]
                self.buffer = self.buffer[2:]

            if len(self.buffer) >= self.length:
                myChunk = self.buffer[:self.length]
                m = Message()
                m.fromStr(myChunk)
                try:
                    d, canceller = self.liveMessages[m.id]
                except KeyError:
                    self.controller.messageReceived(m, self)
                else:
                    del self.liveMessages[m.id]
                    canceller.cancel()
                    try:
                        if self.factory.controller is not None:
                            d, self.factory.controller = self.factory.controller, None
                            message = Message()
                            strio = StringIO.StringIO(myChunk)
                            message.encode(strio)
                            back = strio.getvalue()
                            b = m.toStr()
                            d.callback(b)
                            # d.callback(back)
                            # print 'dir(self.factory):',dir(self.factory.ip)
                            # d.callback(m.toStr())
                    except:
                        log.err()

                self.buffer = self.buffer[self.length:]
                self.length = None
            else:
                break

class DnsClientFactory(DNSClientFactory):
    def clientConnectionFailed(self, connector, reason):
        if self.controller is not None:
            d, self.controller = self.controller, None
            d.errback(reason)       
    def buildProtocol(self, addr):
        p = DnsProtocol(self.controller)
        p.factory = self
        # p.ip = addr
        return p

def getResult(result, ip):
    fp = open('success','a')
    fp.write(ip+'\t'+result+'\n')
    fp.close()
    # print "&&&&getResult",result,'getResult&&&&'
    # print ip
def getError(reason, ip):
    fp = open('err','a')
    fp.write(ip+'\n')
    fp.close()
    # print "getError",reason

def doWork():
    fp = open('AllIP','r')
    for line in fp.readlines():
        ip = line.replace('\n','')

        d = Deferred()
        factory = DnsClientFactory(d,2)
        reactor.connectTCP(ip, 53, factory)
        d.addCallback(getResult,ip)
        d.addErrback(getError,ip)

        yield d


def finish(igo):
    reactor.callLater(5, reactor.stop)

#############################################
def taskRun():
    deferreds = []
    coop = task.Cooperator()
    work = doWork()
    maxRun = 50000
    for i in xrange(maxRun):
        d = coop.coiterate(work)
        deferreds.append(d)
    dl = defer.DeferredList(deferreds, consumeErrors=True)
    dl.addCallback(finish)


#############################################

def main():
    taskRun()
    reactor.run()

if __name__ == '__main__':
    main()


