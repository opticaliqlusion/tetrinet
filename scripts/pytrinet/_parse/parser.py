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
This class contains all the functions needed to parse the commands 
received from the clients. 
The functions are located in the self.parsedic, a dictionary which connects
the different commands to the right function.

The dictionary self.plinedic is part of the Pline class. It contains the 
references to the functions whitin that class so self.pline can send the
received string to the right function. 

functions:
team -- update team strings
startgame -- send the startgame string and initialise the fields
cleanup -- cleanup all the variables needed during a game
score -- calculate scoring after a game has ended
endgame -- end a game
statistics -- send statistics to the clients
playerlost -- send playerlost msgs
sd_timer -- called once the sudden_death mode is activated
f -- parse the f-msgs, field updates
sb -- send special blocks updates, and update the scores
gmgs -- send in game msgs
lvl -- handle level updates
default -- no command default, log it and return nothing
'''

import time, random, logging
import field
import pline
import _utils.timer as timer
from _utils.utils import splitmsg
import _utils.utils
import parse_endgame as end

p_log = logging.getLogger('pytrinet.parse')
c = _utils.utils.colors

class Parser(pline.Pline):
    def __init__(self, msg, command, serverstate, user, channel, sock):
        self.msg = msg
        self.userid = user
        self.channel = channel
        self.sock = sock
        self.command = command
        self.serverstate = serverstate
        self.server = serverstate.server
        self.username = self.server[channel]['users'][self.userid]['name']
        self.winlist = serverstate.winlist
        self.players = ''
        self.winnerID = 0
        self.pString = ''
        self.security_level = self.server[channel]['users'][self.userid]['security_level']
        
        # functions defined in the Pline class
        self.plinedic = {
            '/help':        self.help,
            '/identify':    self.identify,
            '/join':        self.join,
            '/j':            self.join,
            '/news':        self.news,
            '/kick':        self.kick,
            '/list':        self.plist,
            '/msg':            self.pmsg,
            '/register':    self.register,
            '/replay':        self.replay,
            '/start':        self.start,
            '/stop':        self.stop,
            '/where':        self.where,
            '/who':            self.who,
            '/winlist':        self.winlistf,
            '/write_winlist':    self.write_winlist
        }

        # functions defined in the Parser class
        self.parserdic = {
            'team':            self.team,
            'pline':        self.pline,
            'startgame':    self.startwrapper,
            'endgame':        self.endgame,
            'f':            self.f,
            'sb':            self.sb,
            'lvl':            self.lvl,
            'gmsg':            self.gmsg,
            'playerlost':    self.playerlost,
            'default':        self.default
        }


    def chanlist(self):
        ''' Send the channel list to the client.
        For some strange reason the gtetrinet client does not yet understood
        this msg if received after initialising.'''
        
        if self.server[self.channel]['users'][self.userid]['init'] < 2:
            self.server[self.channel]['users'][self.userid]['init'] +=1
            return
        EOL = chr(0xFF)
        msg = []
        for key in self.server.keys():
            channel = self.server[key]
            if len(channel['users']) == channel['max_players']:
                OPEN = 'FULL'
            else: 
                OPEN = 'OPEN' 
            if self.server[key]['game_state'] == 'ingame':
                STATE = '{INGAME}'
            else:
                STATE = '{IDLE}'
            msg_max =  '-%d/%d' %(len(channel['users']), \
                channel['max_players'])
            msg_state = '%10s' %(STATE)
            msg_prio = ' (100) '
            msg_desc = '%s' %(channel['topic'])
            msg.append([channel['channelNo'],\
                '(%s) %s%-14s%s [%s%6s%s%s] %-5s       (%s)   %s%s%s'\
                %(channel['channelNo'],\
                c['blue'],key,\
                c['black'], c['green'], OPEN, msg_max, c['black'],\
                ' ',\
                '100',\
                c['red'],channel['topic'],EOL)])
        msg.sort()
        msg_start = 'pline 0 %sTetriNET Channel Lister - (Type %s/join %s#channelname%s)%s' %(c['red'], c['blue'], c['red'], c['blue'], EOL)
        self.sock.netsend.msgPlainUser(msg_start)
        for i in msg:
            self.sock.netsend.msgPlainUser('pline 0 '+i[1])
        
        #### copy from tetrinetx
        #msg1 = 'pline 0 %sTetriNET Channel Lister - (Type %s/join %s#channelname%s)%s' %(c['blue'],c['red'],c['green'],c['blue'],EOL)
        #msg2 = 'pline 0 %s(%s%s%s) %s#%-6s\t%s[%sFULL%s] %s       (%s)   %c%s%s' %(c['blue'],c['red'], '1', c['green'], c['blue'], 'name', c['blue'],c['red'],c['blue'],'extra text', '100',c['black'],'description',EOL)
        #self.sock.netsend.msgPlainUser(msg1)
        #for i in msg:
        #    self.sock.netsend.msgPlainUser(msg2)


    def team(self):
        ''' Update the teams '''
        
        userid, msg = splitmsg(self.msg)
        userid = int(userid)
        self.server[self.channel]['users'][userid]['init']
        if self.server[self.channel]['users'][userid]['init'] == 0:
            self.sock.netsend.playerjoin(self.channel, self.userid)
            self.sock.netsend.motd(self.channel, self.userid)
            self.sock.netsend.msgPlainUser('pline 0 You are now playing in \
                channel: %s' %(self.channel))
            self.server[self.channel]['users'][self.userid]['init'] = 1
        self.server[self.channel]['users'][userid]['team'] = msg
        self.sock.netsend.team(self.channel, userid)
    
    def rungame(self):
        ''' wrapper for /start to start the game with the right user name '''
        
        self.msg = '1 %s' %(self.userid)
        self.startgame()
    
    def startwrapper(self):
        ''' wrapper to make sure /start is always called with a delay '''
        
        start, userid = splitmsg(self.msg)
        if start == '1':
            self.start()
        else:
            self.endgame()

    def startgame(self):
        ''' Start a game, initialise and send the fiedls '''
        
        start, userid = splitmsg(self.msg)
        if start == '1':
            # start a new game
            # make sure we are only called once
            if self.server[self.channel]['game_state'] == 'ingame':
                # game already started...
                return
            # reset the game playing values to their default scores.
            end.cleanup(self.server, self.channel)
            for user in self.server[self.channel]['users'].keys():
                self.server[self.channel]['last_played'][user] = ''
            self.server[self.channel]['game_state'] = 'ingame'
            # set sd mode if necessary
            sd_start = self.server[self.channel]['sd_start']
            if sd_start > 0:
                self.server[self.channel]['sd_timer'] = timer.Timer(sd_start,\
                    self.sd_timer)
                self.server[self.channel]['sd_timer'].start()
            # add users to the playing list
            # and add users to teams
            for users in self.server[self.channel]['users'].keys():
                self.server[self.channel]['playing'].append(users)
                if self.server[self.channel]['teams'] == 'allowed':
                    team = self.server[self.channel]['users'][users]['team']
                    if not team == '':
                        if self.server[self.channel]['teamplay'].has_key(team):
                            self.server[self.channel]['teamplay'][team].\
                                append(users)
                        else:
                            self.server[self.channel]['teamplay'][team] =\
                                [users]
            # set the score value of the channel to the number of players
            self.server[self.channel]['score'] =\
                len(self.server[self.channel]['playing'])
            # send a msg to the players that a game has been requested
            msg = 'New game requested by user %s%s%s' %(c['red'],\
                self.username,c['black'])    
            self.sock.netsend.msgServer(self.channel, userid, msg)
            max_score = 0
            win_users = [i[1] for i in self.server[self.channel]['winlist']]
            for id in self.server[self.channel]['users'].keys():
                if self.server[self.channel]['users'][id]['team'] != '':
                    name = 't'+ self.server[self.channel]['users'][id]['team']
                else:
                    name = 'p' + self.server[self.channel]['users'][id]['name']
                if name in win_users:
                    max_score += self.server[self.channel]['winlist']\
                        [win_users.index(name)][0]
            self.server[self.channel]['winlist_max_score'] = int(max_score \
                / self.server[self.channel]['score'])            
            # set the start time to now
            self.server[self.channel]['starttime'] = time.time()        
            # get a new field
            fld = self.server[self.channel]['field']
            self.sock.netsend.newGame(self.channel, self.userid, fld)
            if self.server[self.channel]['play_field'] == 'random':
                time.sleep(1)
                for i in self.server[self.channel]['users'].keys():
                    msg = 'f %s ' %(i)
                    field = _utils.utils.randomize_field()
                    for j in range(len(field[0])):
                        for k in range(len(field)):
                            msg += field[k][j]
                    sock = self.server[self.channel]['users'][i]['socket']        
                    sock.netsend.msgPlainUser(msg)
                    sock.netsend.send_to_all(self.channel, i, msg, [i])
        else:
        # not 1 received, thus game ending
            self.endgame()


    def endgame(self):
        # wrapper for endgame since it is needs to be run from serverstate too...
        end.endgame(self.server, self.channel, self.userid, self.winlist)
    

    def playerlost(self):
        ''' Send all players a playerlost msg '''
        
        msg = 'playerlost %s' %(self.userid)
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)
        self.server[self.channel]['playing'].remove(self.userid)
        teamname = self.server[self.channel]['users'][self.userid]['team']
        if self.server[self.channel]['teams'] == 'allowed':
            if teamname != '': 
                self.server[self.channel]['teamplay'][teamname].\
                    remove(self.userid)
                if len(self.server[self.channel]['teamplay'][teamname]) == 0:
                    self.server[self.channel]['teamplay'].pop(teamname)
            if len(self.server[self.channel]['teamplay']) == 1: 
                key= self.server[self.channel]['teamplay'].keys()[0]
                teams = self.server[self.channel]['teamplay'][key]
                players = self.server[self.channel]['playing']
                teams.sort() 
                players.sort()
                if teams == players:
                    end.stat(self.server, self.channel, self.userid)
                    self.endgame()
                    return
        end.stat(self.server, self.channel, self.userid)
        if self.server[self.channel]['type'] == '7tris':
            if len(self.server[self.channel]['playing']) == 0:
                self.endgame()
        elif len(self.server[self.channel]['playing']) <= 1:    
            # either one or zero players left
            self.endgame()
    
    def sd_timer(self):
        ''' The Sudden Death timer send add lines at predefined intervals '''
        
        # test if this is the first time sd is called
        if not self.server[self.channel]['sd_state']:
            p_log.debug('Suddendeath mode enabled.') 
            msg = 'gmsg Time is up, suddendeath mode activated'
            self.sock.netsend.send_to_all(self.channel, self.userid, msg)
            self.server[self.channel]['sd_state'] = 1

        # and send the first add line...
        sd_lines = self.server[self.channel]['sd_lines']
        sd_interval = self.server[self.channel]['sd_interval']
        self.server[self.channel]['sd_timer'] = timer.Timer(sd_interval,\
            self.sd_timer)
        self.server[self.channel]['sd_timer'].start()
        t = time.time() - self.server[self.channel]['starttime']
        msg = 'gmsg You have been playing %u seconds' %(t-1)
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)
        msg = 'sb 0 cs%s 0' %(sd_lines)
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)

    def update_field(self, user, msg):
        ''' Update the servers knowledge of the players field '''
        i = 0
        if (ord(msg[0]) < 33) or (ord(msg[0]) > 47):
            row = 0
            col = 0
            cols = 0
            for j in msg:
                if cols > 11:
                    row += 0
                    col = 0
                    cols = 0
                self.server[self.channel]['users'][int(user)]['game_field']\
                    [row][col] = j
                cols += 1
                col += 1
            return
        while i < len(msg):
            # go trough the whole string
            if (ord(msg[i]) >= 33) and (ord(msg[i]) <= 47):    
                blocktype = _utils.utils.blocks[msg[i]]
                i += 1
            col = _utils.utils.columns[msg[i]]
            row = _utils.utils.rows[msg[i+1]]
            self.server[self.channel]['users'][int(user)]['game_field'][row]\
                [col] = blocktype    
            i += 2

    def f(self):
        ''' Send the field updates and add statistics info for the user. '''
        user, msg = splitmsg(self.msg)
        self.server[self.channel]['users'][self.userid]['nBlocks'] += 1
        if self.server[self.channel]['type'] == '7tris':
            if self.server[self.channel]['users'][self.userid]['nTetris'] >= 7:
                self.endgame()
        self.update_field(user,msg)
        self.server[self.channel]['last_played'][int(user)] += msg         
        self.server[self.channel]['last_played'][int(user)] += 'Z'
        msgstr = 'f %s %s' %(user, msg)
        self.sock.netsend.send_to_all(self.channel,user,msgstr,[int(user)])

    def sb(self):
        ''' Send special blocks and update the statistics '''
        X, btype, Y = self.msg.split(' ',2)
        if btype == 'cs4':
            self.server[self.channel]['users'][self.userid]['nTetris'] += 1
            if self.server[self.channel]['type'] == '7tris':
                player = self.server[self.channel]['users'][self.userid]['name']
                tetri = self.server[self.channel]['users'][self.userid]\
                    ['nTetris']
                msg = 'gmsg Player %s has %s tetri(s)' %(player, tetri)
                self.sock.netsend.send_to_all(self.channel, '0', msg)  
                # forget the special blocks
                return
        if self.server[self.channel]['type'] == '7tris':
            # stop parsing specials, since they are not allowed in here...
            return
        if self.server[self.channel]['type']== 'random': 
            if int(X) > 0 and len(self.server[self.channel]['playing']) > 2:
                X = self.server[self.channel]['playing'][int(random.random() *\
                    len(self.server[self.channel]['playing']))]
        not_to = [self.userid]
        if btype[:2] == 'cs':
            if not self.server[self.channel]['users'][self.userid]\
                    ['team'] == '':
                if self.server[self.channel]['teams'] == 'allowed':
                    if len(self.server[self.channel]['teamplay']) > 0:
                        teamname = self.server[self.channel]['users']\
                            [self.userid]['team']
                        not_to = self.server[self.channel]['teamplay'][teamname]
        msg = 'sb %s %s %s' %(X, btype, Y)
        self.sock.netsend.send_to_all(self.channel, self.userid, msg,\
            not_to)

    def gmsg(self):
        ''' Send in game msgs to all players ''' 
        
        msg = 'gmsg %s' %(self.msg)
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)

    def lvl(self):
        ''' Update the average levels '''
        
        msg = 'lvl %s'
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)

    def default(self):
        ''' A unknown command is received, log it and do nothing... '''
        
        p_log.debug('msg recieved, but no command defined!')
        p_log.debug('command: %s string: %s' %(self.command,self.msg))
