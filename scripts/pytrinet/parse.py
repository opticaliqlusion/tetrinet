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
function which handles the parsing of data. 
It calls the class parser from the _parse module, which handles all the 
commands received from the clients (including field msgs).
Whitin the class parser, a class pline handles the chatline commands and 
messages. 
'''

import logging
import time
import field
import clienthandler
from _utils.utils import splitmsg
import _parse.parser as parser

p_log = logging.getLogger('pytrinet.parser')

    
def dataparse(msg, serverstate, channel, userid, init_str=0 ):
    if init_str: 
        p_log.debug('INIT string received')
        userid, channel = serverstate.new_client(init_str)
        return userid, channel
    # first split the msg 1 two parts, if that succeeds, the msg was a command
    # else the msg was either a endgame string, or a init string, but the init
    # string should have been parsed already...
    command, strn = splitmsg(msg)
    command.strip()
    strn.strip()
    sock = serverstate.server[channel]['users'][userid]['socket']
    parse = parser.Parser(strn, command, serverstate, userid, channel, sock)
    if command in parse.parserdic:
        parse.parserdic[command]()
        return parse.userid, parse.channel
    else:    
        parse.parserdic['default']()
        return parse.userid, parse.channel
    if msg[0:7] != 'endgame':
        p_log.debug('Hu? what did we receive?: %s' %(msg))
    return userid, channel    
