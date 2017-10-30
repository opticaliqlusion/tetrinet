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
This class binds the server to the listening port and allowed upto 5
clients connecting at the same time. 

functions:
handle_accept -- once a connection is accepted, send it to clienthandler
'''

import asyncore, asynchat, socket
import logging

import clienthandler

socket_log = logging.getLogger('pytrinet.sock')

class ServerSocket(asyncore.dispatcher):
    def __init__(self, port, serverstate):
        self.serverstate = serverstate
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((socket.gethostname(), port))
        self.listen(5)

    def handle_accept(self):
        ''' Send accepted connections to the clienthandler '''
        
        new_socket, address = self.accept()
        socket_log.debug("Connecion from %s" %(address[0]))
        client = clienthandler.ClientHandler(new_socket, self.serverstate)
