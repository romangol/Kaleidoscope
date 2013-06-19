# -*- coding: utf-8 -*- 
# 中文支持

import re
import pylab
from ioAnalyzer import *

RegSet = set(["eax", "ebx", "ecx", "edx", "edi", "esi", "ebp", "esp",
               "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl",
               "ax", "bx", "cx", "dx", "si", "di", "bp" ])


def reg_extend( r ):
    if len(r) == 2 and ('x' in r or 'h' in r or 'l' in r):
        return "e" + r[0] + "x"
    elif len(r) == 2:
        return "e" + r
    return r

def fill_splitter( s ):
    if s != "" and s[len(s) - 1] != '|':
        s += '|'
    return s


def draw_bar_plot(X, Y):
    pylab.plot(X, Y, "g.")
    #pylab.ylim(-1.25,+1.25)
    pylab.show()

def mspaint(addrMap):
    X = []
    Y = []

    for k,v in  addrMap.iteritems():
        res = v.split('|')
        res = set(res)
        if len(res) > 1:
            X.append(k)
            Y.append( len(res) )
            #if len(res) > 100: print k, res

    draw_bar_plot( X, Y )


def symbol_dependency( data ):
    addrMap = {}
    regMap = {}
    for i in RegSet: regMap[i] = i
    
    for item in data:
        s = item.strip('\n').split('|')[1]

        if ':' in s: # assign operation
            src = s.split(':')[1]
            dest = s.split('=')[0]

            # assign symbol to mem
            if which_type( dest ) == MEM_TYPE:
                addr = int ( dest[1:9], 16 )
                if not (addr in addrMap): # init a new addr slot
                    addrMap[addr] = ""
                if which_type( src ) == REG_TYPE: #[xxxxxxxx]=REG
                    src = reg_extend(src) # let dx, di, ah, etc --> edx, edi, eax, etc
                    addrMap[addr] = regMap[src] # extend the addr slot
                if which_type( src ) == IMM_TYPE: #[xxxxxxxx]=0xDEADBEEF
                    addrMap[addr] = "0x" + src # assign symbol to addr
                    print addr, "0x" + src
                if which_type( src ) == MEM_TYPE: #[xxxxxxxx]=[xxxxxxxx]
                    addrMap[addr] = src
                addrMap[addr] = fill_splitter( addrMap[addr] )


            # assign symbol to reg
            if which_type( dest ) == REG_TYPE: #REG=[xxxxxxxx]
                dest = reg_extend(dest)

                if which_type( src ) == MEM_TYPE:
                    addr = int ( src[1:9], 16 )
                    if addr in addrMap: # the address is used at least once
                        regMap[dest] = addrMap[addr] # closure passing
                    elif addr in inDic: # this addr must be an input data
                        regMap[dest] = src
                    else:
                        raise NameError, "read mem not in Input"
                if which_type( src ) == IMM_TYPE:
                    regMap[dest] = "0x" + src

                if which_type( src ) == REG_TYPE:
                    regMap[dest] = regMap[src]

                regMap[dest] = fill_splitter( regMap[dest] )

        elif ',' in s: # arithmetic and compare operation
            op = s.split()[0]
            src, dest = s.split()[1].split(',')
            if which_type( dest ) == REG_TYPE:
                regMap[dest] += op + '|'
                if which_type( src ) == IMM_TYPE:
                    regMap[dest] += '0x' + src + '|'

            if which_type( dest ) == MEM_TYPE:
                addr = int ( dest[1:9], 16 )
                if not addr in addrMap: addrMap[addr] = ""
                addrMap[addr] += op + '|'
                if which_type( src ) == IMM_TYPE:
                    addrMap[addr] += '0x' + src + '|'


            if which_type( src ) == REG_TYPE:
                regMap[src] += op + '|'

            if which_type( src ) == MEM_TYPE:
                addr = int ( src[1:9], 16 )
                if not addr in addrMap: addrMap[addr] = ""
                addrMap[addr] += op + '|'

    for k,v in  addrMap.iteritems(): print "%08x-%s"%(k,v)

def numeric_dependency( data ):
    addrMap = {}
    regMap = { "eax":1, "ebx":1, "ecx":1, "edx":1, "edi":1, "esi":1, "ebp":1, "esp":1,
           "ah":1, "al":1, "bh":1, "bl":1, "ch":1, "cl":1, "dh":1, "dl":1,
           "ax":1, "bx":1, "cx":1, "dx":1, "si":1, "di":1, "bp":1 }    

    for item in data:
        s = item.split('|')[1]

        if ':' in s: # assign operation
            src = s.split(':')[1]
            dest = s.split('=')[0]

            if which_type( dest ) == MEM_TYPE:
                addr = int ( dest[1:9], 16 )
                if not (addr in addrMap): # init a new addr slot
                    addrMap[addr] = 1
                if which_type( src ) == REG_TYPE: #[xxxxxxxx]=REG
                    src = reg_extend(src) # let dx, di, ah, etc --> edx, edi, eax, etc
                    addrMap[addr] = regMap[src] # extend the addr slot
                if which_type( src ) == IMM_TYPE: #[xxxxxxxx]=0xDEADBEEF
                    addrMap[addr] = 1
                if which_type( src ) == MEM_TYPE: #[xxxxxxxx]=[xxxxxxxx]
                    addr2 = int ( src[1:9], 16 )
                    if not addr2 in addrMap: addrMap[addr2] = 1
                    addrMap[addr] = addrMap[addr2]


            # assign symbol to reg
            if which_type( dest ) == REG_TYPE: #REG=[xxxxxxxx]
                dest = reg_extend(dest)
                if which_type( src ) == MEM_TYPE:
                    addr = int ( src[1:9], 16 )
                    if addr in addrMap: # the address is used at least once
                        regMap[dest] = addrMap[addr] # closure passing
                    elif addr in inDic: # this addr must be an input data
                        regMap[dest] = 1
                if which_type( src ) == IMM_TYPE:
                    regMap[dest] = 1
                if which_type( src ) == REG_TYPE:
                    regMap[dest] = regMap[src]
                    
        elif ',' in s: # arithmetic and compare operation
            op = s.split()[0]
            src, dest = s.split()[1].split(',')
            if which_type( dest ) == REG_TYPE:
                regMap[dest] += 1
            if which_type( dest ) == MEM_TYPE:
                addr = int ( dest[1:9], 16 )
                if not (addr in addrMap): # init a new addr slot
                    addrMap[addr] = 1
                else:
                    addrMap[addr] += 1
            if which_type( src ) == REG_TYPE:
                regMap[src] += 1
            if which_type( src ) == MEM_TYPE:
                addr = int ( src[1:9], 16 )
                if not (addr in addrMap): # init a new addr slot
                    addrMap[addr] = 1
                else:
                    addrMap[addr] += 1

    for k,v in  addrMap.iteritems():
        print "%08x-%d, "%(k,v),
    print
        
if __name__=="__main__":
    f = open("../data/rw0.log")
    insts = f.readlines()
    inDic = get_input( insts )
    outDic = get_output( insts )
    f.close()
    
    f = open("../data/mil0.log")
    data = f.readlines()
    f.close()
    #numeric_dependency( data )

    symbol_dependency( data )
    
