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

''' This class handles the msgs send by the server to the clients. The 
server information is imported from the clienthandler and used as a 
server dictionary here. 

Colors used in the msgs are imported from the utils module, utils.colors

functions:
send_to_all -- send a string to all connected clients (in the same channel)
playerjoin -- sends playerjoin, playernum msgs
playerleft -- sends playerleave msgs
team -- sends team msgs
motd -- writes the motd of the day (should be imported from the conf. file)
winlist -- sends the winlist to the client
chanlist -- sends a list of all the (active) channels on the server
newGame -- sends newgame and the initialising field string
endGame -- sends endgame to all clients
msgAll -- sends a pline msg to all from a single user
msgPlainUser -- sends a single plain msg to a single user
msgServer -- sends a pline msg from the server to all clients
'''

import asyncore, asynchat, socket
import logging
import _utils.utils as utils
import config
import time

ns_log = logging.getLogger('pytrinet.nets')

class NetworkSend:
    def __init__(self, clienthandler):
        self.clienthandler = clienthandler
        self.server = clienthandler.serverstate.server
        self.c = utils.colors
    
    def send_to_all(self, channel, userid, msg, not_to=[]):
        ''' Send a msg to all users in the same channel '''
        
        self.users = self.server[channel]['users'].keys()
        for userid in self.users:
            if int(userid) not in not_to:
                # user not in not_to    
                sock = self.server[channel]['users'][int(userid)]['socket']
                sock.send_to_client(msg)

    def playerjoin(self, channel, userid):
        ''' Send join strings '''
        
        # let the new player get his userid
        # and send all the others players info to this player
        for id in self.server[channel]['users'].keys():
            if id != int(userid):
                msg = 'playerjoin %s %s' %(id, self.server[channel]['users']\
                    [id]['name'])
                self.clienthandler.send_to_client(msg)
                msg = 'team %s %s' %(id, self.server[channel]['users'][id]\
                    ['team'])
                self.clienthandler.send_to_client(msg)
        
        # send to all players that the player joined the game    
        username = self.server[channel]['users'][int(userid)]['name']
        msg = "playerjoin %s %s" %(userid, username)
        self.send_to_all(channel, userid, msg)
        if self.server[channel]['game_state'] == 'ingame':
            msg = 'playerlost %s' %(userid)
            self.send_to_all(channel, userid, msg)
            self.msgPlainUser('ingame')    
            for i in self.server[channel]['users'].keys():
                if i == int(userid):
                    break
                else:
                    msg = 'f %s ' %(i)
                    field = self.server[channel]['users'][i]['game_field']
                    for i in range(len(field)):
                        for j in range(len(field[0])):
                            msg += field[i][j]
                self.clienthandler.send_to_client(msg)
    
    def playerleft(self, channel, userid):
        ''' Send playerleave msgs '''
        
        msg = "playerleave %s" %(userid)
        self.send_to_all(channel, userid, msg, [userid])

    def team(self, channel, userid):
        ''' Send team msgs '''
        
        team = self.server[channel]['users'][userid]['team']
        msg = "team %s %s" %(userid, team)
        self.send_to_all(channel, userid, msg, [int(userid)])

    def motd(self, channel, userid):
        ''' Send the MOTD msg ''' 
        
        msg = config.motd
        for text in msg:
            self.clienthandler.send_to_client('pline 0 '+text)

    def winlist(self,channel, userid):
        ''' Send the winlist to the client '''
        
        wl =  self.server[channel]['winlist']
        msg = 'winlist'
        max  = len(wl)
        start = 0
        if len(wl) >= 15:
            max =  15
        for i in range(start, max):
            msg += " %s;%s" %(wl[i][1], wl[i][0])
        self.send_to_all(channel, userid, msg) 
    

    def newGame(self, channel, userid, field):
        ''' Send a newgame string, including the initialising field '''
        
        msg = "newgame %s" %(field)
        self.send_to_all(channel, userid, msg)
    
    def endGame(self, channel, userid):
        ''' Send an end-game string '''
        
        self.send_to_all(channel, userid, 'endgame')

    def msgAll(self, channel, userid, msgstring):
        ''' Send a msg to everybody in the channel '''
        
        msg = "pline %s %s" %(userid, msgstring)
        self.send_to_all(channel, userid, msg, [userid])
    
    def msgPlainUser(self, msg):
        ''' Send a plain msg to the user '''
        
        self.clienthandler.send_to_client(msg)

    def msgServer(self, channel, userid, msgstring):
        ''' Send a msg from pline 0 to all'''
        
        msg = "pline 0 %s" %(msgstring)
        self.send_to_all(channel, userid, msg)
        

