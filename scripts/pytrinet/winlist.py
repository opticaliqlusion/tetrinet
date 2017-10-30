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
This class handles the winlist. When the server starts, it reads the 
winlist from file and during winlist updates it writes the winlist back to 
file. 
Before the server shutsdown, the winlist is written to a backup file. 

functions:
swap -- swap the data (pos1 becomes pos2 in a list)
readfile -- read a file with winlist data
newlist -- create a new winlist for a channel
seven -- writes the 7-tris scoring
update -- updates the winlist in memory
writefile -- writes the winlist to file, backup or normal
'''

import logging
import time

# log module for class serverstate
w_log = logging.getLogger('pytrinet.win')

class WinList:
    def __init__(self,winlistFile):
        self.file = winlistFile
        self.backup = winlistFile + '.backup'
        self.winlist = {}
        self.writing = 0
        self.data = ''
    
    def swap(self,l):
        ''' swap two entries from the winlist.
        Since the winlist is stored as pUSER;120 and sorting is done numaricly,
        the name and score has to be swapped. This is done here. '''
        a1 = l[1]
        a2 = l[0]
        return [int(a1),a2]

    def readfile(self):
        ''' read the winlist from file, the filename is given in the config.py
        script '''
        w_log.info('Initialise the winlist')
        f = file(self.file,'r')
        self.data = f.readlines()
        f.close
        #self.pickler(self.file)
        for line in self.data:
            parts = line.split()
            self.winlist[parts[0]] = []
            for i in range(1,len(parts)):
                self.winlist[parts[0]] += [self.swap(parts[i].split(';'))] 

    def newlist(self,channel):
        ''' a new channel needs a new winlist... '''
        self.winlist[channel] = []
    
    def seven(self, channel, pt, time):
        ''' handles the 7tris winfile (shortest time is highest score)'''
        success = 0
        for i in self.winlist[channel]:
            if i[1] == pt:
                if i[0] > time:
                    i[0] = int(round(time))
                success = 1    
        if success == 0:
            self.winlist[channel].append([int(round(time)), pt])
        self.winlist[channel].sort()
        self.writefile()

    def test(self):
        w_log.debug('test to see if we are writing...')
        if self.writing:
            w_log.debug('going to sleep for a second...')
            time.sleep(1)
            self.test()
            

    def update(self, channel, user, time=0, team='', gametype='', score=1):
        ''' update a winlist. Calles the specialised winlist functions if needed
        This function receives already the score which has to be added to the
        winlist.'''
        self.test()    
        if team != '':
            pt = 't' + team
        else: 
            pt = 'p' + user
        
        if gametype == '7tris':
            self.seven(channel, pt, time)
            return
        
        success = 0
        if not time:
            for i in self.winlist[channel]:
                if i[1] == pt:
                    i[0] += score
                    success =1
            if not success:
                self.winlist[channel].append([score,pt])
        else:
            for i in self.winlist[channel]:
                if i[1] == pt:
                    if i[0] < time:
                        i[0] = int(round(time))
                    success = 1
            if not success:
                self.winlist[channel].append([int(round(time)),pt])
        self.winlist[channel].sort()
        self.winlist[channel].reverse()
        self.writefile()
    
    def writefile(self, backup=False, filename=False):
        ''' write the winlist to the winlistfile or backupfile. '''
        if backup:
            w_log.debug('writing backup')
            d_file = self.backup
        else:
            d_file = self.file
            if self.writing:
                w_log.debug('not writing winlist, already doing so')
                return
        if filename:
            d_file = filename
            w_log.debug('writing winlist to filename: %s' %(filename))
        self.writing = 1
        msg = ''
        for k in self.winlist.keys():
            if len(self.winlist[k]) == 0:
                break
            msg += str(k) 
            for item in self.winlist[k]:
                msg += " %s;%s" %(item[1],item[0])
            msg += '\n'    
        if len(msg) > 3:
            f = file(d_file, 'w+')
            f.write(msg)
            f.close()
        self.writing = 0

if __name__ == "__main__":
    wl = WinList('winlist.data')
    wl.readfile()
    wl.update('#coma-lonely','arggg',time=123)
    #print wl.winlist
    wl.writefile()
