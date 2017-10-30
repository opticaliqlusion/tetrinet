import socket
import time

# This is handy but also check out telnetlib

class Connection(object):
    @property
    def recv(self):
        raise NotImplementedError('recv() must be implemented.')
    
    @property
    def send(self):
        raise NotImplementedError('send() must be implemented.')

    @property
    def close(self):
        raise NotImplementedError('close() must be implemented.')

class TcpConnection(Connection):
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.setblocking(0)

    def close(self):
        self.socket.close()
        self.socket = None

    def recv(self,timeout=.5):
        total_data = []
        data = b''
        begin = time.time()

        while 1:
            #if you got some data, then break after wait sec
            if (total_data and time.time() - begin > timeout):
                break
            #if you got no data at all, wait a little longer
            elif (time.time() - begin > timeout * 2):
                break
            try:
                data = self.socket.recv(8192)
                if data:
                    total_data.append(data)
                    begin = time.time()
                #else:
                #   time.sleep(0.1)
            except:
                pass
        return b''.join(total_data)

    def send(self, data):
        self.socket.sendall(data)

    def interact(self):
        while (1):
            data = input('>')
            if('' == data):
                break
            raw_data = bytes(data, 'utf-8')
            if ('\\n' == data):
                raw_data = b''
            print('Sending', raw_data)
            self.socket.sendall(raw_data + b'\n')
            print(self.recv())

def main():
    HOST = '172.16.136.160'
    PORT = 49681
    t = TcpConnection(HOST, PORT)
    #print(t.recv())
    t.interact()
    t.close()

if __name__ == '__main__':
    main()
