# http://blog.csdn.net/ren911/article/details/5313145

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer

class MulticastClientUDP(DatagramProtocol):
    def datagramReceived(self, datagram, address):
        print "Received:" + repr(datagram)

reactor.listenUDP(0, MulticastClientUDP()).write('UniqueID',('192.168.100.2', 9999))
reactor.run()
