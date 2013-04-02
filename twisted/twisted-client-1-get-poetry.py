#!/usr/bin/env python
#-*- coding=utf-8 -*-

import errno
import socket
from twisted.internet import main

class PoetrySocket(object):
    poem = ''
    def __init__(self, task_num, address):
        self.task_num = task_num
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        self.sock.setblocking(0) #设置为非阻塞模式
        from twisted.internet import reactor
        reactor.addReader(self) #把socket传给reactor
    def fileno(self): #返回我们想监听的文件描述符
        try:
            return self.sock.fileno()
        except socket.error:
            return -1
    def connectionLost(self, reason):
        self.sock.close()
        # stop monitoring this socket
        from twisted.internet import reactor
        reactor.removeReader(self)
        # see if there are any poetry sockets left
        for reader in reactor.getReaders():
            if isinstance(reader, PoetrySocket):
                return
        reactor.stop() # no more poetry
    def doRead(self):
        bytes = ''
        while True:
            try:
                bytesread = self.sock.recv(1024)
                if not bytesread:
                    break
                else:
                    bytes += bytesread
            except socket.error, e:
                if e.args[0] == errno.EWOULDBLOCK:
                    break
                return main.CONNECTION_LOST
        if not bytes:
            print 'Task %d finished' % self.task_num
            return main.CONNECTION_DONE
        else:
            msg = 'Task %d: got %d bytes of poetry from %s'
            # print  msg % (self.task_num, len(bytes), self.format_addr())
        self.poem += bytes
    def logPrefix(self):
        return 'poetry'
    def format_addr(self):
        host, port = self.address
        return '%s:%s' % (host or '127.0.0.1', port)

if __name__ == '__main__':
    sock1 = PoetrySocket(1,('127.0.0.1',10000))
    sock2 = PoetrySocket(2,('127.0.0.1',10001))
    sock3 = PoetrySocket(3,('127.0.0.1',10002))

    sockets = [sock1, sock2, sock3]

    from twisted.internet import reactor
    reactor.run()

    for i, sock in enumerate(sockets):
        print 'Task %d: %d bytes of poetry' % (i + 1, len(sock.poem))