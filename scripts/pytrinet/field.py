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
This class generates the initialising field strings, where the number of
blocks are defined, the stack and classicrules etc. 

functions
default -- returns a default field
nospecials -- returns a field without specials
'''

class Field:
    def __init__(self):
        ''' the numbers needed to print a default field. '''
        self.blocks = {
            'stack':'0',
            'startinglevel':'1',
            'linesperlevel':'2',
            'levelincrease':'1',
            'linesperspecial':'1',
            'specialadded':'1',
            'specialcapacity':'18',
            'blockstring1':15,
            'blockstring2':15,
            'blockstring3':14,
            'blockstring4':14,
            'blockstring5':14,
            'blockstring6':14,
            'blockstring7':14,
            'specialstring1':33,    
            'specialstring2':20,
            'specialstring3':1,
            'specialstring4':13,
            'specialstring5':1,
            'specialstring6':15,
            'specialstring7':1,
            'specialstring8':6,
            'specialstring9':10,
            'averagelevels':'1',
            'classicrules':'1'
            }

    def default(self, **options):
        ''' if default receive some dictionary options, default will change the
        default field settings to those define in the optional dictionary. '''
        std = self.blocks.copy()
        if options:
            for key in options.keys():
                std[key] = options[key]
                
        field = ''
        field += std['stack'] + ' '
        field += std['startinglevel'] +  ' ' 
        field += std['linesperlevel'] + ' '
        field += std['levelincrease'] +  ' ' 
        field += std['linesperspecial'] +  ' ' 
        field += std['specialadded'] +  ' ' 
        field += std['specialcapacity'] +  ' ' 
        field += '1' * std['blockstring1'] 
        field += '2' * std['blockstring2']
        field += '3' * std['blockstring3']
        field += '4' * std['blockstring4']
        field += '5' * std['blockstring5']
        field += '6' * std['blockstring6']
        field += '7' * std['blockstring7'] +  ' ' 
        field += '1' * std['specialstring1']
        field += '2' * std['specialstring2']
        field += '3' * std['specialstring3']
        field += '4' * std['specialstring4']
        field += '5' * std['specialstring5']
        field += '6' * std['specialstring6']
        field += '7' * std['specialstring7']
        field += '8' * std['specialstring8']
        field += '9' * std['specialstring9'] +  ' ' 
        field += std['averagelevels'] +  ' ' 
        field += std['classicrules'] +  ' ' 
        return field

    def nospecials(self):
        ''' returns a field with 'linesperspecial == 0' '''
        return self.default(linesperspecial='0', specialadded='0')

    def suddendeath(self):
        return self.default(startinglevel='15', levelincrease='4')

if __name__ == "__main__":
    f = field()
    #print f.default()
    #print f.nospecials()
    #print f.default2()
    #print f.default()
             


