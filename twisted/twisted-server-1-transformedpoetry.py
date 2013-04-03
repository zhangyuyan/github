from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver

class TransformService(object):
    def cummingsify(self, poem):
        return poem.lower()

class TransformProtocol(NetstringReceiver):
    def stringReceived(self, request):
        if '.' not in request: # bad request
            self.transport.loseConnection()
            return
        xform_name, poem = request.split('.', 1)
        self.xformRequestReceived(xform_name, poem)
        print poem
    def xformRequestReceived(self, xform_name, poem):
        new_poem = self.factory.transform(xform_name, poem)
        if new_poem is not None:
            self.sendString(new_poem)
        self.transport.loseConnection()

class TransformFactory(ServerFactory):
    protocol = TransformProtocol
    def __init__(self, service):
        self.service = service
    def transform(self, xform_name, poem):
        thunk = getattr(self, 'xform_%s' % (xform_name,), None)
        if thunk is None: # no such transform
            return None
        try:
            return thunk(poem)
        except:
            return None # transform failed
    def xform_cummingsify(self, poem):
        return self.service.cummingsify(poem)

if __name__ == '__main__':
    service = TransformService()
    factory = TransformFactory(service)
    from twisted.internet import reactor
    port = reactor.listenTCP(11000, factory,interface='localhost')
    print 'Serving transforms on %s.' % (port.getHost(),)
    reactor.run()
