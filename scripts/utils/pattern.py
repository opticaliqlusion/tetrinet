#!/usr/bin/env python

import sys
import struct

class Pattern(object):
    def __init__(self, length):
        self._set_a = b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        self._set_b = b'abcdefghijklmnopqrstuvwxyz'
        self._set_c = b'0123456789'
        self.length = length

        self._idx_a = 0
        self._idx_b = 0
        self._idx_c = 0
        self.pattern = b''

        while (len(self.pattern) < self.length):
            self.pattern += (bytes([self._set_a[self._idx_a]]) + 
                             bytes([self._set_b[self._idx_b]]) + 
                             bytes([self._set_c[self._idx_c]]))
            
            self._idx_c += 1

            if (self._idx_c == len(self._set_c)):
                self._idx_c = 0
                self._idx_b += 1
            
            if (self._idx_b == len(self._set_b)):
                self._idx_b = 0
                self._idx_a += 1
            
            if (self._idx_a == len(self._set_a)):
                self._idx_a = 0

    def __repr__(self):
        return self.pattern

    def offset(self, val, endian='le'):
        fmt = '<I'
        if ('le' != endian):
            fmt = '>I'
        chunk = struct.pack(fmt, int(val, 16))
        return self.pattern.index(chunk)

def main():
    length = int(sys.argv[1])
    p = Pattern(length)
    print(p.pattern)
    part = input('Enter part:')
    print(p.offset(part))

if __name__ == '__main__':
    main()
