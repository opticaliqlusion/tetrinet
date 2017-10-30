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
Parser endgame helper functions.
The endgame helper functions needed by the parser class and some others..
'''

import time
import _utils.utils 

c = _utils.utils.colors

def cleanup(server, channel):
    ''' Set the ingame veriables to their default values '''
    # cleansup the mess after a game has finished.
    server[channel]['playing']=[]
    server[channel]['game_state']=''
    if server[channel]['sd_timer']:
        server[channel]['sd_timer'].stop()
    #for each user, reset the scores to 0:
    for user in server[channel]['users'].keys():
        server[channel]['users'][user]['nTetris'] = 0
        server[channel]['users'][user]['nBlocks'] = 0
            
    # remove teams
    server[channel]['teamplay'] = {}
    # reset the game-state

def statistics(server, channel, userid, t):
    ''' Send statistics about the game to all players '''
    players = server[channel]['playing']
    if server[channel]['type'] == '7tris':
        players = [userid]
    for id in server[channel]['users'].keys():
        sock = server[channel]['users'][id]['socket']
        if len(players) == 1:
            blocks = server[channel]['users'][players[0]]\
                ['nBlocks']
            name = server[channel]['users'][players[0]]\
                ['name']
            msg = 'pline 0 Comrade %s%s%s dropped %s blocks in %1.0f seconds'\
                %(c['red'], name, c['black'], blocks, t)
            sock.netsend.msgPlainUser(msg)
            msg = 'pline 0 Comrade %s%s%s managed to play %s tetri(s)'\
                %(c['red'], name, c['black'], server[channel]['users']\
                [players[0]]['nTetris'])
            sock.netsend.msgPlainUser(msg)
        # reset the block count
    
def stat(server, channel, userid):
    ''' send private statistics to the loosing user. '''
    sock = server[channel]['users'][userid]['socket']
    blocks = server[channel]['users'][userid]['nBlocks']
    tetris = server[channel]['users'][userid]['nTetris']
    played_time = time.time() - server[channel]['starttime']
    msg = 'pline 0 You dropped %s%s%s blocks in %1.0f seconds'\
        %(c['blue'], blocks, c['black'], played_time)
    sock.netsend.msgPlainUser(msg)
    msg = 'pline 0 With those blocks you managed to play %s%s%s tetri(s)'\
        %(c['red'], tetris, c['black'])
    sock.netsend.msgPlainUser(msg)

def score(server, channel, userid, winlist, players, t):
    ''' Calculate the scoring for the different users '''
    sock = server[channel]['users'][userid]['socket']
    if server[channel]['type'] == '7tris':
    # 7tris game, no teams possible
        if server[channel]['users'][userid]['nTetris']\
                    >= 7:
            winlist.update(server[channel]\
                ['winlistname'], server[channel]['users']\
                [userid]['name'],t,gametype='7tris')
        stat(server, channel, userid)
        return
    
    wl = server[channel]['winlist']
    wl_users = [i[1] for i in wl]
    max_score = server[channel]['winlist_max_score']
    no_players = server[channel]['score']
    if server[channel]['teams'] == 'allowed' and \
            len(server[channel]['teamplay']) == 1 and\
            server[channel]['score'] > 1: 
        keys = server[channel]['teamplay'].keys()[0]    
        if len(server[channel]['teamplay'][keys]) == len(players):
            # and only 1 team left
            teamname = server[channel]['teamplay'].keys()[0]
            msg = 'The comrades in the %s%s%s party have won for the people!'\
                %(c['red'],teamname, c['black'])
            name = 't' + teamname
            points = 0
            if name in wl_users:
                pos = wl_users.index(name)
                points = wl[pos][0]
            score = int((max_score - points)/(7 - no_players)) 
            if score < 1:
                score = 1
            winlist.update(server[channel]['winlistname'],\
                server[channel]['users'][userid]['name'], team=teamname,\
                    score=score)
            msg1 = 'The nation rewarded our comrades with %i points' %(score)
            sock.netsend.msgServer(channel, userid, msg)    
            sock.netsend.msgServer(channel, userid, msg1)
            return
    if len(players) == 1:
        #and only 1 player left
        # store the winner name so it can be used by the statistics
        winnerID = players[0]
        msg = 'Comrade %s%s%s has won for the people and the party'\
            %(c['red'],server[channel]['users'][players[0]]['name'],c['black'])
        #update winlist
        if server[channel]['type'] == 'time':
        # time game, no teams
            winlist.update(server[channel]['winlistname'],
                server[channel]['users'][players[0]]['name'],t)
        elif server[channel]['score'] > 1:
            # normal game with more then 1 player
            if server[channel]['teams'] == 'allowed' and \
                    server[channel]['users'][players[0]]['team'] != '':
                teamname = server[channel]['users'][players[0]]['team']
                name = 't' + teamname
            else:
                teamname = ''
                name = 'p' + server[channel]['users'][players[0]]['name']
            points = 0
            if name in wl_users:
                pos = wl_users.index(name)
                points = wl[pos][0]
            score = int((max_score - points)/(7 - no_players)) 
            if score < 1:
                score = 1
            winlist.update(server[channel]['winlistname'],\
                server[channel]['users'][players[0]]['name'], team=teamname,\
                    score=score)
            msg1 = 'The nation rewarded our comrade with %i points' %(score)    
            sock.netsend.msgServer(channel, userid, msg)
            sock.netsend.msgServer(channel, userid, msg1)
    elif len(players) == 0:
        # single player game 
        msg = 'Comrade %s%s%s has won for the people and the party'\
            %(c['red'],server[channel]['users'][userid]['name'],c['black'])
        # only winlist update if time involved
        sock.netsend.msgServer(channel, userid, msg)    
        if server[channel]['type'] == 'time':
            # time game, no teamplay
            winlist.update(server[channel]['winlistname'],\
                server[channel]['users'][userid]['name'],t)
        elif server[channel]['type'] == '7tris':
            if server[channel]['users'][userid]['nTetris']\
                    >= 7:
                winlist.update(server[channel]\
                    ['winlistname'], server[channel]['users']\
                    [userid]['name'],t,type='7tris')
    else:        
    # game ended with more then 1 winner (ie, end-game button was pressed)    
    # or team game played, but team play already delt with...
        pl = ''
        for i in players:
            pl += server[channel]['users'][i]['name'] + ' '
        msg = 'Comrades %s%s%s have survived the game, nobody won'\
            %(c['red'],pl, c['black'])
        sock.netsend.msgServer(channel, userid, msg)    

def endgame(server, channel, userid, winlist):
    ''' The game has  ended, somobody won or pressed the button '''
    #p_log.debug('Game Ended')
    server[channel]['game_state'] = ''      
    # time (in seconds since 1970) how long the game lasted
    t = time.time() - server[channel]['starttime']
    # send the endgame msg to everybody in the channel
    sock = server[channel]['users'][int(userid)]['socket']
    sock.netsend.endGame(channel, userid)
    # all the players still in the game
    players = server[channel]['playing']
    if server[channel]['score']:
        score(server, channel, userid, winlist, players, t)
    # send some statistics
    if len(server[channel]['users'].keys()) > 1:
        statistics(server, channel, userid, t)
        sock.netsend.winlist(channel, userid)
    if len(server[channel]['users'].keys()) > 0:
        sock.netsend.winlist(channel, userid)
    # reset the game state
    cleanup(server, channel)
