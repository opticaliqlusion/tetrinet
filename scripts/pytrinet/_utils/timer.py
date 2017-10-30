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
This class deals with timing. 
Using __init__ the function which will be called once the timing thread runs
out of time is given, as is the function wich will announce the steps or 
once the timer is interrupted. 
'''

import time
import thread
import timer

class Timer:
    def __init__(self, seconds, function, step_function='', stop_function='',\
            step=1 ):
        self.__seconds = int(seconds)
        self.__step = step
        self.__lock = thread.allocate_lock()
        self.__interval = 1
        self.__alive = 0
        self.__loop = 0
        self.function = function
        
        # set the step function (function called after every second)
        if step_function == '':
            self.__stepf = self.default
        else:    
            self.__stepf = step_function
        
        # set the stop function (function called after sending stop signal)    
        if stop_function == '':
            self.__stopf = self.default
        else:
            self.__stopf = stop_function
        

    def start(self):
        ''' start the countdown '''
        self.__lock.acquire()
        if not self.__alive:
            self.__loop = 1
            self.alive = 1
            thread.start_new_thread(self.__run, ())
        self.__lock.release()
    
    def stop(self):
        ''' stop the countdown, calls the stop function '''
        self.__lock.acquire()
        self.__loop = 0
        self.__lock.release()
        self.__stopf(self.__seconds)

    def __run(self):
        ''' countdown is running... '''
        while self.__loop > 0:
            s = self.__seconds - self.__step
            self.__stepf(s + 1)
            time.sleep(self.__step)
            if self.__seconds <= self.__step:
                self.__loop = 0    
                self.function()
                self.__alive = 0    
                return
            self.__seconds -= self.__step
        self.__alive = 0    

    def default(self, seconds):
        ''' default function for stop and step, does nothing '''
        pass

if __name__ == "__main__":

    def final_action(seconds):
        'Time is up!'
    
    def second_action(s):
        'Counting down: %s' %(s)
    
    t = Timer(10,final_action)
    t.start()
    time.sleep(10)
    t = Timer(10,final_action)
