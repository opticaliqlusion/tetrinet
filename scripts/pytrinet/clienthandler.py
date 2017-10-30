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
This class handles incoming connections from the clients. It reads
an incoming stream until it finds the EOL character and then passes on the
data to the parsing class. 

functions:
collect_incoming -- collect the incoming data
found_terminator -- if EOL found, start parsing the data
handle_close -- close connections
send_to_client -- send a packet to the client, with an EOL appended
'''

import asyncore, asynchat
import logging

import networksend
import parse

class ClientHandler(asynchat.async_chat):
    def __init__(self, conn, serverstate):
        self.serverstate = serverstate
        self.server = serverstate.server
        logging.info('Initialising connection')
        asynchat.async_chat.__init__(self,conn)
        self.set_terminator(chr(0xFF))
        self.channel = False
        self.user = False
        self.data = ''
        self.netsend = networksend.NetworkSend(self)

    def collect_incoming_data(self, data):
        ''' Collect incoming data from the client. '''
        
        self.data += data
    
    def found_terminator(self):
        ''' Once a terminator is found (0xFF), send the data to the processing
        class '''
        
        user = self.user
        channel = self.channel
        if (len(self.data) > 30) and (self.data.find(' ') == -1): 
            logging.info('New user initialising') 
            #sending init string to the new_client function    
            self.user,self.channel = self.serverstate.new_client(self,\
                self.data)
        else:    
            self.user, self.channel = parse.dataparse(self.data,\
                self.serverstate,channel, user)
        # clear the data
        self.data = ''

    def handle_close(self):
        ''' Close a connection, remove the player from the field and close
        the socket '''
        
        if len(self.server[self.channel]['users'].keys()) == 0:
            return
        sock = self.server[self.channel]['users'][self.user]['socket']
        self.serverstate.del_client(self.user, self.channel)
        sock.close()

    def send_to_client(self, packet):
        ''' Append 0xFF and send the string to the client '''
        self.send(packet + chr(0xFF))
    
