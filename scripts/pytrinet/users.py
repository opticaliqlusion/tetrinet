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

import config
import crypt

salt = '234asv407gwhlkj'

def encrypt(str, slt=salt):
    return crypt.crypt(str, slt)

def read_users(filename=config.users):
    f = file(filename, 'r')
    data = f.readlines()
    f.close()
    users_dict = {}
    if len(data) == 0:
        return users_dict
    for line in data:
        parts = line.split(';;;') 
        users_dict[parts[0]] = {'level': int(parts[1]),
                                'password': parts[2].strip(),
                                }
    return users_dict                            

def write_users(users_dict, filename=config.users):
    msg = ''
    for key in users_dict.keys():
        msg += key + ';;;' + str(users_dict[key]['level']) + ';;;' + users_dict[key]['password'] + '\n'
    f = file(filename, 'w')
    f.write(msg)
    f.close()
    

