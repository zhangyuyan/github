import  sys
from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.protocols.basic import NetstringReceiver

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
    def __init__(self, deferred):
        self.deferred = deferred
    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)
    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

class TransformClientProtocol(NetstringReceiver):
    def connectionMade(self):
        self.sendRequest(self.factory.xform_name, self.factory.poem)
    def sendRequest(self, xform_name, poem):
        self.sendString(xform_name + '.' + poem)
    def stringReceived(self, s):
        self.transport.loseConnection()
        self.poemReceived(s)
    def poemReceived(self, poem):
        self.factory.handlePoem(poem)

class TransformClientFactory(ClientFactory):
    protocol = TransformClientProtocol
    def __init__(self, xform_name, poem):
        self.xform_name = xform_name
        self.poem = poem
        self.deferred = defer.Deferred()
    def handlePoem(self, poem):
        d, self.deferred = self.deferred, None
        d.callback(poem)
    def clientConnectionLost(self, _, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)
    clientConnectionFailed = clientConnectionLost

class TransformProxy(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
    def xform(self, xform_name, poem):
        factory = TransformClientFactory(xform_name, poem)
        from twisted.internet import reactor
        reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred

def get_poetry(host, port):
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = PoetryClientFactory(d)
    reactor.connectTCP(host, port, factory)
    return d

if __name__ == '__main__':
    addresses = [('127.0.0.1', 10000), ('127.0.0.1', 10001), ('127.0.0.1', 10002)]
    xform_addr = addresses.pop(0)
    proxy = TransformProxy(*xform_addr)
    from twisted.internet import reactor
    poems = []
    errors = []
    def try_to_cummingsify(poem):
        d = proxy.xform('cummingsify', poem)
        def fail(err):
            print >>sys.stderr, 'Cummingsify failed!'
            return poem
        return d.addErrback(fail)
    def got_poem(poem):
        print poem
        poems.append(poem)
    def poem_failed(err):
        print >>sys.stderr, 'The poem download failed.'
        errors.append(err)
    def poem_done(_):
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()
    for address in addresses:
        host, port = address
        d = get_poetry(host, port)
        d.addCallback(try_to_cummingsify)
        d.addCallbacks(got_poem, poem_failed)
        d.addBoth(poem_done)
    reactor.run()
