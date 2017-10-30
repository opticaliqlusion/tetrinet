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
This module contains the class which starts the server, and the setupLog 
function so logging is available troughout the server. 

To start the server, it requires port 31457 to be free, else it will return
with an error message. 
'''

import logging, time
import asyncore

import clienthandler
import serversocket
import serverstate
import winlist
import config
import users

def    setupLog():
    ''' Setup logging for the server '''
    
    loglevels = {
        'NOTSET':     0,
        'DEBUG':    10,
        'INFO' :    20,
        'WARN':        30,
        'WARNING':    30,
        'ERROR':    40,
        'FATAL':    50
        }
    # specila file logging level to log userchanges to file
    # so a webclient can reach the data...
    logging.FILE = 25
    logging.addLevelName(logging.FILE, 'FILE')

    if loglevels.has_key(config.loglevel):
        loglevel = loglevels[config.loglevel]
    else:
        loglevel = loglevels['NOTSET']
    
    # setup file logging to DEBUG
    cs_formatter = logging.Formatter('%(asctime)s %(name)-20s %(lineno)-4d \
        %(levelname)-8s %(message)s', '%Y%m%d %H:%M')
    fh_formatter = logging.Formatter('%(created)s \t %(message)s')
    cs = logging.StreamHandler()
    fh = logging.FileHandler(config.logfile)
    cs.setLevel(loglevel)
    fh.setLevel(logging.FILE)
    cs.setFormatter(cs_formatter)
    fh.setFormatter(fh_formatter)
    
    # create base logger
    logger = logging.getLogger('pytrinet')
    logger.setLevel(loglevel)
    logger.addHandler(cs)
    logger.addHandler(fh)

root_log = logging.getLogger('pytrinet')

class ServerMain:
    ''' This class runs the server '''
    
    def __init__(self,port):
        root_log.info('Starting the server')
        self.serverstate = serverstate.ServerState()
        serversocket.ServerSocket(port, self.serverstate)
        try:
            asyncore.loop()
          except KeyboardInterrupt:
            self.serverstate.winlist.writefile(True)
            root_log.info('Writing users to user.data file')
            users.write_users(self.serverstate.users)
              for key in self.serverstate.server.keys():
                  for user in self.serverstate.server[key]['users'].keys():
                      self.serverstate.del_client(user, key)
              #asyncore.socket_map.clear()
            asyncore.close_all(asyncore.socket_map)
            root_log.info('Server has been shut down')
            
if __name__ == "__main__":
    setupLog()
    s = ServerMain(31457)
