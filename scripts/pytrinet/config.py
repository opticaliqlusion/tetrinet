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
File containing the configuration options for the server
'''

winlist  = 'winlist.data'
users = 'user.data'
channel1 = '#coma'
loglevel = 'INFO'
version = 'PyTrinet version 0.2.1'
logfile = 'pytrinet.log'
motd = ['',
       '********* Message of the Day ********',
       'Welcome to the PyTrinet Server version %s!' %(version) ,
       'This server is written in python by Derek, aka shoe.',
       'For help, type /help',
       'to see a listing of the channels available, type /list',
       'contact info: irc://oudemans/#pytrinet', 
       '']
       
