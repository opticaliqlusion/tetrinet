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
This class keeps track of the state of the server.

data:
self.server -- base containing all server information
self.winlist -- winlist class
self.wl -- winlist containing all the winlists


functions:
initChannels -- initialise the channels
new_channel -- create a new channel
check_channel -- test if a channel has a unique name
check_user -- test if a user has a unique name
add_client -- add a user to a channel
new_client -- initialise a new user
del_client -- remove an user
move_client -- move a client to another player number
set_team -- set the team for a user
'''

# default python libraries:
import logging
import time

import config
import _utils.utils as utils
import winlist
from channels import channelDB  # import the pre-defined channels
import field
import users
import _parse.parse_endgame as end

ss_log = logging.getLogger('pytrinet.server')


class ServerState:
    def __init__(self):
        self.server = {}
        self.winlist = winlist.WinList(config.winlist)
        self.winlist.readfile()
        self.wl = self.winlist.winlist
        ss_log.info('Initialising preconfigured channels')
        self.initChannels()
        ss_log.info('Load registerd users...')
        self.init_users()
        self.orig_chan = ''    
        self.field = field.Field()
    
    def init_users(self):
        ''' initialise registerd users '''
        self.users = users.read_users()
        
    def initChannels(self):
        ''' initialise the channels from the config file (now channels.py) '''
        
        for key in channelDB.keys():
            self.server[key] = channelDB[key]
            if not self.wl.has_key(key):
                self.winlist.newlist(key)
            self.server[key]['winlist'] = self.wl[key]
             
    def new_channel(self, channelname):
        ''' add a new channel to the server '''
        
        if not self.wl.has_key(channelname):
            self.winlist.newlist(channelname)
        channels = len(self.server.keys())+1
        # create a new channel dictionary    
        self.server[channelname] = {
            'channelNo':channels,
            'topic':'On the fly created channel',
            'field':self.field.default(),
            'play_field':'',
            'playing':[],
            'max_players':6,
            'game_state':'',
            'game_timer':'',
            'last_played': {},
            'users':{},
            'teamplay':{},
            'teams':'allowed',
            'type':'',
            'sticky':0,
            'winlistname':channelname,
            'winlist':self.wl[channelname],
            'winlist_max_score':0,
            'score':0,
            'starttime':time.time(),
            'sd_start':120,
            'sd_interval':30,
            'sd_lines':1,
            'sd_timer':'',
            'sd_state':0
            } 
        if self.orig_chan != '':    # there exists an old channel
            self.server[channelname]['max_players'] = self.orig_chan\
                ['max_players']
            self.server[channelname]['type'] = self.orig_chan['type']
            self.server[channelname]['winlist'] = self.orig_chan['winlist']
            self.server[channelname]['winlistname'] = self.orig_chan\
                ['winlistname']
            self.server[channelname]['sd_start'] = self.orig_chan['sd_start']
            self.server[channelname]['sd_interval'] = self.orig_chan\
                ['sd_interval']
            self.server[channelname]['sd_lines'] = self.orig_chan['sd_lines']
            self.server[channelname]['play_field'] = self.orig_chan\
                ['play_field']
            self.server[channelname]['teams'] = self.orig_chan['teams']

    def check_channel(self,channel):
        ''' test  if a channel exists '''
        
        if not self.server.has_key(channel):
            self.new_channel(channel)
        elif len(self.server[channel]['users']) >= (self.server[channel]\
                ['max_players']) :
            self.orig_chan = self.server[channel]
            channel += '1'
            ss_log.debug('Channel full, trying new channel: %s' %(channel))
            channel = self.check_channel(channel)
        return channel    

    def check_user(self, chan, user):
        ''' test if a user exists '''
        
        for id in self.server[chan]['users'].keys():
            if self.server[chan]['users'][id]['name'] == user:
                ss_log.debug('User already exists')
                # give user another name
                username = user + '1'
                user = self.check_user(chan, username)
        return user
    
    def add_client(self, user, sock, team='', channel=config.channel1):
        ''' add a (new) user to a channel '''
        
        chan = self.check_channel(channel)
        username = self.check_user(chan, user)
        # loop trough all possible id's, stop when a empty one if found
        for userid in range(1,7):
            if userid not in self.server[chan]['users']:
                # playernumber did not yet exist
                self.server[chan]['users'][userid] = {'name':username,
                    'team':team,
                    'socket':sock,
                    'nBlocks':0,
                    'nTetris':0,
                    'init':0,
                    'send_list':0,
                    'game_field':[['0' for i in range(12)] for j in range(22)],
                    'security_level':0
                    }
                ss_log.log(logging.FILE,'Adding user: %s  as player %s' %(username, 
                    userid))
                # send winlist
                sock.netsend.winlist(chan, userid)
                # send playernumber
                sock.netsend.msgPlainUser('playernum %s'%(userid))
                # send playerjoin msgs
                sock.netsend.playerjoin(chan, userid)
                break
        return chan, userid

    def new_client(self, socket, init_string, team=''):
        ''' initialise a new client (decrypt string, assign channel '''
        
        start, username, version = utils.decode(init_string)
        channel, userid = self.add_client(username, socket, team)
        return userid,channel

    def del_client(self, userid, channel):
        ''' remove a client from the server '''
        
        if len(self.server[channel]['users'].keys()) == 0:
            # nobody in the channel -> nothing to remove
            return
        ss_log.log(logging.FILE,'Removing user: %s' %(self.server[channel]['users']\
            [userid]['name']))
        userid = int(userid)
        # if a game is running...
        if self.server[channel]['game_state'] == 'ingame':
            # test if the user is playing
            if userid in self.server[channel]['playing']:
                self.server[channel]['playing'].remove(userid)
                if len(self.server[channel]['playing']) == 0:
                    self.server[channel]['users'][userid]['socket'].netsend.\
                        endGame(channel, userid)
                    self.server[channel]['users'][userid]['socket']\
                        .netsend.playerleft(channel, userid)
                    self.server[channel]['users'].pop(userid)
                    end.cleanup(self.server, channel)
                    if not self.server[channel]['sticky']:
                        if len(self.server[channel]['users'].keys()) < 1:
                            self.server.pop(channel)
                    return
                elif len(self.server[channel]['playing']) == 1 \
                        and self.server[channel]['type'] == '':
                    self.server[channel]['users'][userid]['socket']\
                        .netsend.playerleft(channel, userid)
                    self.server[channel]['users'].pop(userid)
                    end.endgame(self.server, channel, self.server[channel]\
                        ['playing'][0], self.winlist)
                    return
        self.server[channel]['users'][userid]['socket']\
            .netsend.playerleft(channel, userid)
        self.server[channel]['users'].pop(userid)
        if self.server[channel]['game_state'] == 'countdown':
            if len(self.server[channel]['users'].keys()) == 0:
                self.server[channel]['game_state'] = ''
                self.server[channel]['game_timer'].stop()
        if not self.server[channel]['sticky']:
            if len(self.server[channel]['users'].keys()) < 1:
                self.server.pop(channel)

    def move_client(self, useridOld, useridNew):
        # used for moving a client within a channel
        ss_log.debug('Move client not yet implemented')
        pass

