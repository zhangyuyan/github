#!/usr/bin/env python
#-*- coding=utf-8 -*-

import datetime
from twisted.internet.protocol import Protocol, ClientFactory

class PoetryProtocol(Protocol):
    poem = ''
    task_num = 0
    def dataReceived(self, data):
        self.poem += data
        msg = '任务 %d: 接受 %d bytes 大小的诗歌 从 %s'
        print  msg % (self.task_num, len(data), self.transport.getPeer())
    def connectionLost(self, reason): #下载诗歌完成后，是安全关闭，还是意外关闭
        self.poemReceived(self.poem)
    def poemReceived(self, poem):   #下载诗歌完成后
        self.factory.poem_finished(self.task_num, poem)

class PoetryClientFactory(ClientFactory):
    task_num = 1
    protocol = PoetryProtocol # tell base class what proto to build
    def __init__(self, poetry_count):
        self.poetry_count = poetry_count
        self.poems = {} # task num -> poem
    def buildProtocol(self, address):
        proto = ClientFactory.buildProtocol(self, address)
        proto.task_num = self.task_num
        self.task_num += 1
        return proto
    def poem_finished(self, task_num=None, poem=None):
        if task_num is not None:
            self.poems[task_num] = poem
        self.poetry_count -= 1
        if self.poetry_count == 0:
            self.report()
            from twisted.internet import reactor
            reactor.stop()
    def report(self):
        for i in self.poems:
            print '任务 %d: %d bytes接受诗歌' % (i, len(self.poems[i]))
    def clientConnectionFailed(self, connector, reason):
        print '连接失败:', connector.getDestination()
        self.poem_finished()

if __name__ == '__main__':
    addresses = [('127.0.0.1', 10000), ('127.0.0.1', 10001), ('127.0.0.1', 10002)]
    factory = PoetryClientFactory(len(addresses))
    from twisted.internet import reactor
    for address in addresses:
        host, port = address
        reactor.connectTCP(host, port, factory) #创建PeotryProtocol实例
    reactor.run()





