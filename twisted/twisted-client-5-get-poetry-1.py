import random, sys
from twisted.internet import defer
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

def get_poetry(host, port):
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = PoetryClientFactory(d)
    reactor.connectTCP(host, port, factory)
    return d

class GibberishError(Exception): pass

class CannotCummingsify(Exception): pass

def cummingsify(poem):
    def success():
        return poem.lower()
    def gibberish():
        raise GibberishError()
    def bug():
        raise CannotCummingsify(poem)
    return random.choice([success, gibberish, bug])()

if __name__ == '__main__':
    addresses = [('127.0.0.1', 10000), ('127.0.0.1', 10001), ('127.0.0.1', 10002)]
    from twisted.internet import reactor
    poems = []
    errors = []
    def cummingsify_failed(err):
        if err.check(CannotCummingsify):
            print 'Cummingsify failed!'
            return err.value.args[0]
        return err
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
        d.addCallback(cummingsify)
        d.addErrback(cummingsify_failed)
        d.addCallbacks(got_poem, poem_failed)
        d.addBoth(poem_done)
    reactor.run()
