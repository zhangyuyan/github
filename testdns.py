from twisted.names.client import AXFRController
from twisted.names.dns import DNSDatagramProtocol
from twisted.names.dns import  Query
from twisted.names.dns import Name
from twisted.names.dns import TXT
from twisted.names.dns import CH

from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.internet import reactor
from twisted.internet import task
from twisted.internet import reactor
reactor.suggestThreadPoolSize(50000)

def finish():
    reactor.callLater(5, reactor.stop)

def getResult(result, ip):
    fp = open('success','a')
    contents = result.toStr()
    print '****************',type(content)
    content = contents.replace('\n','').replace('?','')
    fp.write(ip+'\t'+content+'\n')
    fp.close()

def getError(reason, ip):
    fp = open('err','a')
    fp.write(ip+'\t'+str(reason)+'\n')
    fp.close()

def nexted():
    for i in range(152267):
        yield i+1
a = nexted()

def doWork():
    for ip in file("list12.txt"):
        i = a.next()
        ip = ip.strip()
        d = Deferred()
        name = Name('version.bind')
        axf = AXFRController(name,d)
        dns = DNSDatagramProtocol(axf)
        query = Query()
        query.name = Name('version.bind')
        query.type = TXT
        query.cls = CH
        query = [query]
        d1 = dns.query((ip,53), query)
        d1.addCallback(getResult,ip)
        d1.addErrback(getError,ip)
        yield d1

def finish(igo):
    reactor.callLater(5, reactor.stop)

#############################################
def taskRun():
    deferreds = []
    coop = task.Cooperator()
    work = doWork()
    maxRun = 152264
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

