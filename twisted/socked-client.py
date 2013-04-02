sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost',10000))
poem = ''
while True:
    data = sock.recv(1024)
    poem += data
    if not data:
        sock.close()
        break
print poem