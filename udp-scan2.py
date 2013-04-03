# http://blog.csdn.net/ren911/article/details/5313145

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Helloer(DatagramProtocol):
    def startProtocol(self):
        host = '127.0.0.1'
        port = 9999
        self.transport.connect(host, port)
        print "we can only send to %s now" % str((host, port))
        self.transport.write("helloKao") # no need for address
    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
    def connectionRefused(self):
        print "No one listening"

reactor.listenUDP(0, Helloer())
reactor.run()
