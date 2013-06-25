# -*- coding: utf-8 -*- 
#中文支持

from ioAnalyzer import *
from math import log
from random import randint

MEM_WRITE_RE = '\[[a-z0-9]{8}\]=[a-z0-9]*'
MEM_READ_RE = '[a-z0-9]*:\[[a-z0-9]{8}\]'

# Performs a Shannon entropy analysis on a given block of data.
def shannon( dic ):
    counter = 0
    for i in dic:
        counter += i
    hertz = 0
    base = 0.0
    for i in dic:
        if i != 0:
            hertz = i * 1.0 / counter
            base += hertz * log(hertz, 2)

    if base < 0.0001 and base > -0.0001:
        return 0

    return base / -8


def analyzeEntropy( fp ):
    readDic = {} # 读取输入数据
    writeDic = {} # 写入输出数据

    s = "start"
    memDic = {}
    newData = []
    while s != "":
        s = fp.readline().strip("\n")
        if '?' in s or s == "":
            continue

        memSize = int( s[1] )
        codeAddr = int( s[3:11], 16 )
        memAddr = int( s[13:21], 16 )
        content = s.split('=')[1]
        if 'R' in s: # is memory read
            if not codeAddr in readDic:
                readDic[codeAddr] = [0] * 256
            for j in range( len(content) / 2 ): # each time read one byte
                d = int( content[j * 2 : j * 2 + 2], 16)
                readDic[codeAddr][d] += 1
                
        if 'W' in s: # is memory write
            if not codeAddr in writeDic:
                writeDic[codeAddr] = [0] * 256
            for j in range( len(content) / 2 ): # each time read one byte
                d = int( content[j * 2 : j * 2 + 2], 16)
                writeDic[codeAddr][d] += 1

    print "Finish reading entropy.log!"
    
    f = open("../data/EntropyResult.log", 'w' )
    f.write("#######Input Data#######\n")
    for addr, items in readDic.iteritems():
        f.write( "%08x:%f\n"%(
                addr,
                shannon( items )
            )
        )


    f.write("#######Write Data#######\n")
    for addr, items in writeDic.iteritems():
        f.write( "%08x:%f\n"%(
                addr,
                shannon( items )
            )
        )
    f.close()

    print "Entropy Analysis Done!"

if __name__=="__main__":
    f = open("../data/entropy.log", "r")
    analyzeEntropy(f)
    f.close()


