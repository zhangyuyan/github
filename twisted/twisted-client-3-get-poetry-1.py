import sys
from twisted.internet.protocol import Protocol, ClientFactory

class PoetryProtocol(Protocol):
    poem = ''
    def dataReceived(self, data):
        self.poem += data
    def connectionLost(self, reason):
        self.poemReceived(self.poem)
    def poemReceived(self, poem):
        self.factory.poem_finished(poem)

class PoetryClientFactory(ClientFactory):
    protocol = PoetryProtocol
    def __init__(self, callback, errback):
        self.callback = callback
        self.errback = errback
    def poem_finished(self, poem):
        self.callback(poem)
    def clientConnectionFailed(self, connector, reason):
        self.errback(reason)

def get_poetry(host, port, callback, errback):
    from twisted.internet import reactor
    factory = PoetryClientFactory(callback, errback)
    reactor.connectTCP(host, port, factory)

if __name__ == '__main__':
    addresses = [('127.0.0.1', 10000), ('127.0.0.1', 10001), ('127.0.0.1', 10002)]
    from twisted.internet import reactor
    poems = []
    errors = []
    def got_poem(poem):
        poems.append(poem)
        poem_done()
    def poem_failed(err):
        print >>sys.stderr, 'Poem failed:', err
        errors.append(err)
        poem_done()
    def poem_done():
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()
    for address in addresses:
        host, port = address
        get_poetry(host, port, got_poem, poem_failed)
    reactor.run()
    for poem in poems:
        print poem