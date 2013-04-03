# http://blog.csdn.net/ren911/article/details/5313145

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

class MulticastServerUDP(DatagramProtocol):
    def startProtocol(self):
        print 'Started Listening'
        self.transport.joinGroup('192.168.100.2')
    def datagramReceived(self, datagram, address):
        if datagram == 'UniqueID':
            print "Server Received:" + repr(datagram)
            self.transport.write("data", address)

reactor.listenMulticast(9999, MulticastServerUDP())
reactor.run()
