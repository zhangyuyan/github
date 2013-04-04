import optparse, os
from twisted.internet.protocol import ServerFactory, Protocol

class PoetryProtocol(Protocol):
    def connectionMade(self):
        self.transport.write(self.factory.poem)
        self.transport.loseConnection()

class PoetryFactory(ServerFactory):
    protocol = PoetryProtocol
    def __init__(self, poem):
        self.poem = poem

if __name__ == '__main__':
    poem = open('/Users/mc813/Desktop/twisted/twisted-intro/poetry/ecstasy.txt').read()
    factory = PoetryFactory(poem)
    from twisted.internet import reactor
    port = reactor.listenTCP(10008, factory)
    print 'Serving ecstasy.txt on %s.' % port.getHost()
    reactor.run()
