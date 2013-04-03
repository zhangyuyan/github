# http://blog.csdn.net/ren911/article/details/5313145

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

class Echo(DatagramProtocol):
    def datagramReceived(self, data, (host, port)):
        print "received %r from %s:%d" % (data, host, port)
        data = data+' udp-scan1.py '
        self.transport.write(data, (host, port))
reactor.listenUDP(9999, Echo())
reactor.run()

