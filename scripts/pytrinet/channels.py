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

import time
import field

channelDB = {}
fl = field.Field()

channelDB['#coma'] = {
    'channelNo':1,
    'topic':'Default rules',
    'playing':[],
    'field':fl.default(),
    'last_played':{},
    'play_field':'',
    'max_players':6,
    'game_state':'',
    'game_timer':'',
    'users':{},
    'teams':'allowed',
    'teamplay':{},
    'type':'',
    'sticky':1,
    'winlistname':'#coma',
    'winlist':'',
    'winlist_max_score':0,
    'score':0,
    'starttime':time.time(),
    'sd_timeout':120,
    'sd_start':120,
    'sd_interval':30,
    'sd_lines':1,
    'sd_timer':'',
    'sd_state':0
    } 

channelDB['#coma-lonely'] = { 
    'channelNo':2,
    'topic':'Default rules, time played is your place in the winlist',
    'playing':[],
    'max_players':1,
    'field':fl.suddendeath(),
    'last_played':{},
    'play_field':'',
    'game_state':'',
    'game_timer':'',
    'users':{},
    'teams':'no',
    'teamplay':{},
    'type':'time',
    'sticky':1,
    'winlist':'',
    'winlistname':'#coma-lonely',
    'winlist_max_score':0,
    'score':0,
    'starttime':time.time(),
    'sd_timeout':1,
    'sd_start':1,
    'sd_interval':15,
    'sd_lines':1,
    'sd_timer':'',
    'sd_state':0
    } 


channelDB['#coma-7tris'] = {
    'channelNo':3,
    'topic': '7 times tetris and you win',
    'playing':[],
    'field':fl.nospecials(),
    'last_played':{},
    'play_field':'',
    'max_players':6,
    'game_state':'',
    'game_timer':'',
    'users':{},
    'teams':'no',
    'teamplay':{},
    'type':'7tris',
    'sticky':1,
    'winlist':'',
    'winlistname':'#coma-7tris',
    'winlist_max_score':0,
    'score':0,
    'starttime':time.time(),
    'sd_timeout':0,
    'sd_start':0,
    'sd_interval':0,
    'sd_lines':0,
    'sd_timer':'',
    'sd_state':0
    }


channelDB['#coma-random'] = {
    'channelNo':4,
    'topic': 'Random specials, random field, play with 3 or more players!',
    'playing':[],
    'field':fl.default(),
    'last_played':{},
    'play_field':'random',
    'max_players':6,
    'game_state':'',
    'game_timer':'',
    'users':{},
    'teams':'no',
    'teamplay':{},
    'type':'random',
    'sticky':1,
    'winlist':'',
    'winlistname':'#coma-random',
    'winlist_max_score':0,
    'score':0,
    'starttime':time.time(),
    'sd_timeout':120,
    'sd_start':120,
    'sd_interval':30,
    'sd_lines':1,
    'sd_timer':'',
    'sd_state':0
    }
