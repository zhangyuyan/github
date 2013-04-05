#!/usr/bin/env python
#-*- coding=utf-8 -*-

from twisted.names.dns import DNSDatagramProtocol
from twisted.names.dns import Message
from twisted.names.dns import  Query
from twisted.names.dns import Name
from twisted.names.dns import Record_TXT
from twisted.internet.defer import Deferred
from twisted.internet import reactor
import random
from twisted.internet import  task
from twisted.internet import defer
import struct
from twisted.internet.error import CannotListenError

class DnsDatagramProtocol(DNSDatagramProtocol):

    def __init__(self, controller, ip = '', reactor=None, datagram = ''):
        self.controller = controller
        self.id = random.randrange(2 ** 10, 2 ** 15)
        if reactor is None:
            from twisted.internet import reactor
        self._reactor = reactor
        self.ip = ip 
        self.datagram = datagram

    def startProtocol(self):
        self.liveMessages = {}
        self.resends = {}
        
        qd = Query()
        qd.name = Name('version.bind')
        qd.type = 16
        qd.cls = 3
        qd = [qd]
    
        self.query((self.ip, 53), qd)  

#############################################
def getResult(result):
    print result
def getError(reason):
    err = reason.getErrorMessage()
#############################################    
def doWork():
    fp = open("AllIP",'r')
    for ip in fp.readlines():
        ip = ip.strip().replace('\n','')
        d = Deferred()
        reactor.listenUDP(0,DnsDatagramProtocol(d, ip))
        # d.callbacks(finish)
        yield d


def finish(igo):
    print "Out of finish!"
    reactor.callLater(5, reactor.stop)


#############################################
def taskRun():
    deferreds = []
    coop = task.Cooperator()
    work = doWork()
    maxRun = 50
    for i in xrange(maxRun):
        d = coop.coiterate(work)
        # d.addCallback(getResult)
        # d.addErrback(getError)
        deferreds.append(d)
    dl = defer.DeferredList(deferreds)
    dl.addCallback(finish)


#############################################

def main():
    taskRun()
    reactor.run()

if __name__ == '__main__':
    main()


