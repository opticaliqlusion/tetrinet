#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2006 Derek Land (derek@ddmr.nl)
# This file is part of PyTrinet.

# PyTrinet is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# PyTrinet is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

''' 
Module containing various functions needed troughout the server. 
This module also contains the color definitions. 
'''

from sys import *
import random

def security(level_user, level_req, sock):
    if level_user < level_req:
        msg = 'pline 0 Do you belong to the party?'
        sock.netsend.msgPlainUser(msg)
        return 1
    return 0

def splitmsg(msg):
    ''' returns a string splitted in 2. If there is a ValueError, splitmsg 
    returns -1. '''
    if msg.find(' ') != -1:
        a, b = msg.split(' ',1)
    else:
        a = '-1'
        b = '-1'
    return a, b

def dec2hex(dec):
    ''' convert a dec number to hex, with leading 0 '''
    s = hex(dec)[2:]
    if len(s) < 2:
        s = '0' + s
    return s


# login string looks like "tetrifaster <user> <version>"
# ex: tetrifaster TestUser 1.13

def encode(nick, version, ip):
    dec = 2
    s = 'tetrisstart %s %s' % (nick, version)
    h = str(54*ip[0] + 41*ip[1] + 29*ip[2] + 17*ip[3])
    encodeS = dec2hex(dec)
    
    for i in range(len(s)):
        dec =  (( dec + ord(s[i])) % 255) ^ ord(h[i % len(h)])
        s2 = dec2hex(dec)
        encodeS += s2

    return encodeS


def findHash(encodeI):
    ''' Find the hash in the encrypted string using the information from the 
    first part of the string, ie the word 'tetrisstar'. '''
    #s = 'tetrisstar'
    s = [0x74, 0x65, 0x74, 0x72, 0x69, 0x73, 0x73, 0x74, 0x61, 0x72, 0x74,0x20]
    h = [0 for i in s]

    for i in range(len(s)):
        h[i] = (( s[i] + encodeI[i]) % 255) ^ encodeI[i+1]
    l = 11
    for i in range(l,0,-1):
        for j in range(len(s)-l):
            if h[j] != h[j+l]:
                l = l -1
    return h

def decode(encodeH):
    ''' Decode the init string recieved from the tetrinet clients.
    This string contains the protocol version, nickname, ip number of the server
    and a random number.
    The ipaddress from the server is used to encrypt the string, together with a
    random number. This ip address is not checked against the running ip address,
    so even if the server is forwarderd to another machine, it still works. '''
    if len(encodeH) %2 != 0:
        ''' encode string has not the right size'''
        exit('argh... broken string')
    
    #parse the hex values into a string
    encodeI = [0 for i in range(len(encodeH)/2)]
    for i in range(1,len(encodeI)):
        encodeI[i] = ( int(encodeH[i*2]+encodeH[i*2+1],16) )

    h = findHash(encodeI)
    s = []
    for i in range(1,len(encodeI)):
        x = ( ( (encodeI[i] ^ h[(i-1) % len(h)]) + 255 - encodeI[i -1]) % 255) 
        s.append(chr(x))
    
    ss =''
    for i in s:
        ss += i
    return ss.split()


def randomize_field(): 
    field = [['0' for i in range(22)] for j in range(12)]
    blocks = ['0', '1', '2', '3', '0', '4', '5', 'o','0', '1', '2', '0', '3',\
        '4', '5', '0', '1', '0', '2', '3', '4', '5', '0', '1', '2', '0', '3',\
        '4', '5','0','0','0','0']
    for i in range(12,21):
        for j in range(12):
            field[j][i] = blocks[int(random.random()*len(blocks))]
    return field        

# dictonary containing the colors used in the game. 
colors = {
    'bold':chr(0x1F),
    'italic':chr(0x0B),
    'underline':chr(0x15),
    'cyan':chr(0x03),
    'black':chr(0x04),
    'blue':chr(0x05),
    'gray':chr(0x06),
    'magenta':chr(0x08),
    'green':chr(0x17),
    'lime':chr(0x0E),
    'silver':chr(0x0F),
    'maroon':chr(0x10),
    'dark blue':chr(0x11),
    'olive':chr(0x12),
    'purple':chr(0x13),
    'red':chr(0x14),
    'teal':chr(0x0C),
    'white':chr(0x18),
    'yellow':chr(0x19)
    }

# dictionary for looking up the coordinates of a column of a players field
columns = {
    chr(ord('3')):0,
    chr(ord('3')+1):1,
    chr(ord('3')+2):2,
    chr(ord('3')+3):3,
    chr(ord('3')+4):4,
    chr(ord('3')+5):5,
    chr(ord('3')+6):6,
    chr(ord('3')+7):7,
    chr(ord('3')+8):8,
    chr(ord('3')+9):9,
    chr(ord('3')+10):10,
    chr(ord('3')+11):11
}

# dictionary for looking up the coordinates of a row of a players field
rows = {
    chr(ord('H')-21):0,
    chr(ord('H')-20):1,
    chr(ord('H')-19):2,
    chr(ord('H')-18):3,
    chr(ord('H')-17):4,
    chr(ord('H')-16):5,
    chr(ord('H')-15):6,
    chr(ord('H')-14):7,
    chr(ord('H')-13):8,
    chr(ord('H')-12):9,
    chr(ord('H')-11):10,
    chr(ord('H')-10):11,
    chr(ord('H')-9):12,
    chr(ord('H')-8):13,
    chr(ord('H')-7):14,
    chr(ord('H')-6):15,
    chr(ord('H')-5):16,
    chr(ord('H')-4):17,
    chr(ord('H')-3):18,
    chr(ord('H')-2):19,
    chr(ord('H')-1):20,
    chr(ord('H')):21
}

# ascii codecs of the blocks used by the client
blocks = {
    '!':'0',
    '"':'1',
    '#':'2',
    '$':'3',
    '%':'4',
    '&':'5',
    "'":'a',
    '(':'c',
    ')':'n',
    '*':'r',
    '+':'s',
    ',':'b',
    '-':'g',
    '.':'q',
    '/':'o'
}

if __name__ == "__main__":
    ip1 = [129,125,101,198]
    ip2 = [129,125,101,199]
    ip3 = [10,1,6,152]
    ip4 = [10,0,0,152]
    nick = 'shoe '
    version = '1.13 '
    ip = [ip1, ip2, ip3, ip4]
    for i in ip:
        msg = encode(nick, version, i)
        decode(msg)
    #print '00479F25A23F81C50F4386CBDE61FA5BF52565A2E629'
    #print decode('00479F25A23F81C50F4386CBDE61FA5BF52565A2E629')

