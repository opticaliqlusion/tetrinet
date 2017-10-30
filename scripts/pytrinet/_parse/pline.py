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
This class parses the pline (chat) msgs. 
First it deduce if the msg starts with a /, ifso, it is a command and 
should be executed with the arguments provided after the command. 
If it is not a command, it should be send to all other users in the channel,
don't send it again to the same user, else the user will receive the msg
twice.

functions:
winlist -- display winlist of this or another channel
help -- display help
plist -- send the channel listing to the user
join -- join another channel
start -- start a game (with default time-out of 3 sec)
pmsg -- send pline chat msg to only 1 user
where -- show in which channel the client is currently
who -- shows who are connected to the server (all channels)
pline -- parses the input, send a msg to the user if no command defined
'''
import logging

from _utils.utils import splitmsg
import _utils.timer as timer
import _utils.utils
import users
import time

p_log = logging.getLogger('pytrinet.pline')

c = _utils.utils.colors

class Pline:
    def winlistf(self):
        ''' Send the winlist to a user '''
        
        offset = 0
        if self.pString != '':
            if self.pString.isdigit():
                chan = self.server[self.channel]['winlistname']
                offset = int(self.pString)
            else:
                chan, offset = splitmsg(self.pString)
                if chan == '-1':
                    chan = self.pString
                if not offset.isdigit():
                    offset = 0
        else:
            chan = self.server[self.channel]['winlistname']
        if self.winlist.winlist.has_key(chan):
            wl =  self.winlist.winlist[chan]
        else:
            msg = 'pline 0 %sWinlist %s does not yet exists%s' %(c['red'],\
                chan,c['black'])
            self.sock.netsend.msgPlainUser(msg) 
            return 
        msg = 'pline 0 Winlist for channel: %s%s%s' %(c['red'],chan,c['red'])
        self.sock.netsend.msgPlainUser(msg) 
        max = len(wl)
        offset = int(offset)
        if len(wl) < 11:
            offset = 0
        elif max - offset < 1:     
            offset = max - 10
        elif max - offset > 10:
            max  = offset + 10
        if offset > 0:
            offset -= 1

        for i in range(offset, max):
            if wl[i][1][0] == 't':
                name = c['green'] + 'team ' + c['blue'] + wl[i][1][1:]
            else:
                name = wl[i][1][1:]
            msg = "pline 0 %s%3s%s %-20s %s%5s%s" %(c['red'],i+1,c['blue'],\
                name,c['red'],wl[i][0],c['black'])
            self.sock.netsend.msgPlainUser(msg) 

    def news(self):
        ''' send recent news updates'''
        
        msg = []
        msg.append('pline 0 Recent news, changes bugs:')
        msg.append('pline 0 2006-11-27: Fixed blinking of the block when a \
            line is added')
        msg.append('pline 0 2006-11-26: Added #coma-random, a randomized \
            channel.')
        msg.append('pline 0 2006-11-26: Almost fixed: teamplay. ')
        [self.sock.netsend.msgPlainUser(i) for i in msg]

    def help(self):
        ''' Send a brief help msg '''
        msg= []
        msg.append('pline 0 The following commands are available on this \
            server:') 
        msg.append(('pline 0 %s/help%s: explains some of the basic commmands')\
            %(c['green'],c['black']))
        msg.append(('pline 0 %s/join %sname%s: lets you jump to another \
            channel')%(c['green'],c['blue'],c['black']))
        msg.append(('pline 0 %s/list%s: lists all available channels')\
            %(c['green'],c['black']))
        msg.append(('pline 0 %s/start %sn%s: starts the game after n seconds \
            (defaults to 3 seconds)')%(c['green'],c['blue'],c['black']))
        msg.append(('pline 0 %s/stop%s: stop countingdown for a new game')\
            %(c['green'],c['black']))
        msg.append(('pline 0 %s/winlist %sname%s: shows the current winlist')\
            %(c['green'],c['blue'],c['black']))
        msg.append(('pline 0 %s/msg %s[1-6]%s msg%s: send msg to user 1 -- 6 \
            (only 1 user allowed)')%(c['green'], c['blue'],c['red'],c['black']))
        msg.append(('pline 0 %s/news%s: display recent news')%(c['green'],\
            c['black']))    
        [self.sock.netsend.msgPlainUser(i) for i in msg]

    def plist(self, plain=0):
        ''' Send the channel list to the client '''
        self.chanlist()

    def join(self):
        ''' Join another channel, which means leaving the current one '''
        
        if self.channel == self.pString:
            return
        p_log.debug('moving player to channel %s if possible' %(self.pString))
        oldChannel = self.channel
        team = self.server[oldChannel]['users'][self.userid]['team']
        # remove from old channel
        for id in self.server[oldChannel]['users'].keys():
            self.sock.netsend.msgPlainUser('playerleave %s' %(id))
        self.serverstate.del_client(int(self.user), oldChannel)
        # move to new channel
        self.channel, self.userid = self.serverstate.add_client(self.username,\
            self.sock, team, self.pString)
        if self.server.has_key(oldChannel):
            if not self.server[oldChannel]['sticky']:
                if len(self.server[oldChannel]['users'].keys()) < 1:
                    self.server.pop(oldChannel)

    def start_msg(self, seconds):
        msg = 'pline 0 Game starting in %s%s%s seconds' %(c['green'],seconds,\
            c['black'])
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)

    def stop(self):
        if self.server[self.channel]['game_timer']:
            self.server[self.channel]['game_timer'].stop()

    def stop_msg(self, secs):
        if self.server[self.channel]['game_state'] == 'countdown':
            self.server[self.channel]['game_state'] = ''
        msg = 'pline 0 Game countdown %sstopped%s'%(c['red'], c['black']) 
        self.sock.netsend.send_to_all(self.channel, self.userid, msg)

    def start(self):
        ''' Start a game with a certain countdown '''
        # need to be rewritten to make use of the new timer class
        if self.server[self.channel]['game_state'] == 'countdown':
            msg = 'pline 0 Game already started'
            msg2 = 'pline 0 type /stop to stop the countdown.'
            self.sock.netsend.msgPlainUser(msg)
            self.sock.netsend.msgPlainUser(msg2)
            return    
        if self.server[self.channel]['game_state'] == 'ingame':
            msg = 'pline 0 You have to wait, another game is already running'
            self.sock.netsend.msgPlainUser(msg)
            return
        self.server[self.channel]['game_state'] = 'countdown'    
        t = 3
        if self.pString.isdigit():
            t = int(self.pString)
            if int(self.pString) > 50:
                t = 5
        self.server[self.channel]['game_timer'] = timer.Timer(t,\
            self.rungame, self.start_msg, self.stop_msg) 
        self.server[self.channel]['game_timer'].start()

    def pmsg(self):
        ''' Send a private msg to another user on the same channel '''
        if not self.pString:
            return
        user, msg = splitmsg(self.pString)    
        if not user.isdigit() or not self.server[self.channel]['users']\
                .has_key(int(user)):    
            self.sock.netsend.msgPlainUser('pline 0 Please use the\
                comrades number instead of the name')
            return
        if msg == '--- MARK ---':
            self.plist()
        else: 
            msgstr = 'pline %s %s' %(self.userid, msg)
            sock = self.server[self.channel]['users'][int(user)]['socket']    
            sock.netsend.msgPlainUser(msgstr)

    def where(self):
        ''' Returns the current location of the user '''
        msg = 'pline 0 You are in: %s%s%s' %(c['green'],self.channel,c['black'])
        self.sock.netsend.msgPlainUser(msg)

    def who(self):
        ''' Returns a list of all the channels with all the users connected '''
        for channel in self.server.keys():
            if len(self.server[channel]['users'].keys()) > 0:
                msg = 'pline 0  %s%-10s%s' %(c['red'],channel,c['black'])
                self.sock.netsend.msgPlainUser(msg)
            for user in self.server[channel]['users'].keys():
                username = self.server[channel]['users'][user]['name']
                msg = 'pline 0  %20s' %(username)
                self.sock.netsend.msgPlainUser(msg) 
    
    def kick(self):
        if _utils.utils.security(self.security_level, users.levels['kick'], self.sock):
            return
        ''' removes a user from the server... '''
        msg = ''
        user, msg = splitmsg(self.pString)
        if not user.isdigit() or not self.server[self.channel]['users'].\
                has_key(int(user)):
            send_msg = 'pline 0 The user does not exist'
            self.sock.netsend.msgPlainUser(send_msg)
            return
        send_msg = 'pline 0 You have been kicked by %s with the following reason: %s'%(self.server[self.channel]['users'][self.userid]['name'], msg)
        sock = self.server[self.channel]['users'][int(user)]['socket']
        sock.netsend.msgPlainUser(send_msg)
        sock.handle_close()

    def write_winlist(self):
        if _utils.utils.security(self.security_level, users.levels['write_winlist'], self.sock):
            return
        ''' write the winlist to file'''
        if self.pString == '':
            msg = 'pline 0 Winlist written to default file'    
            self.serverstate.winlist.writefile()
        else:
            msg = 'pline 0 Winlist written to file: %s' %(self.pString)    
            self.serverstate.winlist.writefile(filename=self.pString)
        self.sock.netsend.msgPlainUser(msg)    
            
    def register(self):
        ''' register a username '''
        if self.pString == '':
            msg = 'pline 0 Send a password to register your username'
            self.sock.netsend.msgPlainUser(msg)
            return
        #first test if a username already excists
        username = self.server[self.channel]['users'][self.user]['name']    
        if self.serverstate.users.has_key(username):
            msg1 = 'pline 0 This name is already registerd.'
            msg2 = 'Use \identify to identify yourself'
            self.sock.netsend.msgPlainUser(msg1)
            self.sock.netsend.msgPlainUser(msg2)
            return
        self.serverstate.users[username] = {'password': users.encrypt(self.pString), 
                                            'level':1,
                                            'last_seen':0}
                                            
        self.server[self.channel]['users'][self.user]['security_level'] = 1
        msg = 'pline 0 Comrade %s registered with password: ******' %(username)
        self.sock.netsend.msgPlainUser(msg)
        
    def identify(self):
        ''' identify a username '''
        if self.pString == '':
            msg = 'pline 0 Send a password to identify your username'
            self.sock.netsend.msgPlainUser(msg)
            return
        username = self.server[self.channel]['users'][self.user]['name']    
        if not self.serverstate.users.has_key(username):
            msg = 'pline 0 Register your username first...'
            self.sock.netsend.msgPlainUser(msg)
            return
        if users.encrypt(self.pString) == self.serverstate.users[username]['password']:
            level = self.serverstate.users[username]['level']
            self.server[self.channel]['users'][self.user]['security_level'] = level
            self.serverstate.users[username]['last_seen'] = 0
            msg = 'pline 0 You are now identified'
        else:
            msg = 'pline 0 Password did not match...'
        self.sock.netsend.msgPlainUser(msg)

    def replay(self):
        ''' send all the data received about the game '''
        if self.pString.isdigit() and int(self.pString) < 7 and int(self.pString) > 0:
            if self.server[self.channel]['last_played'].has_key(int(self.pString)):
                msg = self.server[self.channel]['last_played'][int(self.pString)]
                while len(msg) > 500:
                    self.sock.netsend.msgPlainUser('pline 0 ' + msg[:500])
                    msg = msg[500:]
                if len(msg) > 0:    
                    self.sock.netsend.msgPlainUser('pline 0 ' + msg)
            self.sock.netsend.msgPlainUser('pline 0 You have to play a game first...')
        else:
            if not self.server[self.channel]['last_played'].has_key(int(self.user)):
                self.sock.netsend.msgPlainUser('pline 0 You have to play a game first...')
            msg = self.server[self.channel]['last_played'][self.user]
            while len(msg) > 500:
                self.sock.netsend.msgPlainUser('pline 0 ' + msg[:500])
                msg = msg[500:]
            if len(msg) > 0:    
                self.sock.netsend.msgPlainUser('pline 0 ' + msg)
        
    def pline(self):
        ''' Parse the pline msgs, send a plain msg if no command defined '''
        user, msg = splitmsg(self.msg)
        if not user:
            p_log.debug('error in pline msg: %s' %(self.msg))
            return
        self.user = int(user)
        if msg[0:1] == '/':
            command, strn = splitmsg(msg)
            if command in self.plinedic:
                self.pString = strn.strip()
                return self.plinedic[command]()
            else:
                if msg in self.plinedic:
                    return self.plinedic[msg]()
                else:
                    return self.help()
        else:
            msgstr = 'pline %s %s' %(user, msg)
            self.sock.netsend.send_to_all(self.channel, user, msgstr, \
                [int(user)])

