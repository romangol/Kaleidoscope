# -*- coding: utf-8 -*- 
# 中文支持

import re
import pylab
from ioAnalyzer import *

RegSet = set(["eax", "ebx", "ecx", "edx", "edi", "esi", "ebp", "esp",
               "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl",
               "ax", "bx", "cx", "dx", "si", "di", "bp" ])

DataDic = {}

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

def change_dic( s, content, addFlag = False ):
    sType = which_type( s )
    if sType == MEM_TYPE:
        addr = int ( s[1:9], 16 )
        if addFlag == True:
            if not addr in DataDic:
                DataDic[addr] = content
            else:
                DataDic[addr] += content
        else:
            DataDic[addr] = content
    elif sType == REG_TYPE: #REG=[xxxxxxxx]
        if addFlag == True:
            DataDic[reg_extend(s)] += content
        else:
            DataDic[reg_extend(s)] = content
    else:
        raise NameError, s
    
def get_content(s):
    sType = which_type( s )
    result = ""
    if sType == REG_TYPE: #[xxxxxxxx]=REG
        result = DataDic[reg_extend(s)] # extend the addr slot
    elif sType == MEM_TYPE: #[xxxxxxxx]=[xxxxxxxx]
        addr = int ( s[1:9], 16 )
        result = s
    elif sType == IMM_TYPE: #[xxxxxxxx]=0xDEADBEEF
        result = s
    else:
        raise NameError, s

    if result  != "" and result[-1] != '|':
        result += '|'
    return result

def symbol_dependency( data ):
    for i in RegSet: DataDic[i] = i + '|'
    
    for item in data:
        s = item.strip('\n').split('|')[1]

        if ':' in s: # assign operation
            src = s.split(':')[1]
            dest = s.split('=')[0]

            #if which_type( src ) == IMM_TYPE: continue

            change_dic( dest, get_content(src) )

        elif ',' in s: # arithmetic and compare operation
            try:
                op, dest, src = s.split()
            except:
                raise NameError, s
            dest = dest.strip(',')
            #if which_type( src ) == IMM_TYPE: continue
            #if op == "cmp": continue

            d = op + '-' + get_content(src)
            change_dic( dest, d, True )
        #else: raise NameError, s

    for k,v in  DataDic.iteritems():
        if not k in RegSet:
            print "%08x:%s"%(k,v)

if __name__=="__main__":
    f = open("../data/mil0.log")
    data = f.readlines()
    f.close()
    #numeric_dependency( data )

    symbol_dependency( data )
    
