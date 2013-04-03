#!/usr/bin/env python

# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import defer, task
import sys

from twisted.internet import reactor
reactor.suggestThreadPoolSize(50000)
#############################################
class SMTPClient(LineReceiver):
    def lineReceived(self, line):
        ip =  self.transport.getPeer().host,
        self.transport.loseConnection()
        self.factory.scanFinished(ip[0] + " " + line+" Cyber")
#############################################
class SMTPClientFactory(ClientFactory):
    protocol = SMTPClient
    def __init__(self, deferred):
        self.deferred = deferred

    def scanFinished(self, banner):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(banner)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)
#############################################
def getResult(result,mx):
    print mx,result
def getError(reason,mx):
    err = reason.getErrorMessage()
#############################################    
def doWork():
    i = 1
    fp = file("smtp.log", 'w')
    for mx in file("mx.short.txt"):
        mx = mx.strip().split()[1]
        d = defer.Deferred()
        factory = SMTPClientFactory(d)
        reactor.connectTCP(mx, 25, factory)
        d.addCallback(getResult,mx)
        d.addErrback(getError,mx)
        logRecord = "%d\t%s\n" %(i, mx)
        i += 1
        fp.write(logRecord)
        fp.flush()
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
    dl = defer.DeferredList(deferreds)
    dl.addCallback(finish)


#############################################

def main():
    taskRun()
    reactor.run()

if __name__ == '__main__':
    main()
