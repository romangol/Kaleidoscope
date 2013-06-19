# -*- coding: utf-8 -*- 
#中文支持

from ioAnalyzer import *
from math import log
from random import randint

MEM_WRITE_RE = '\[[a-z0-9]{8}\]=[a-z0-9]*'
MEM_READ_RE = '[a-z0-9]*:\[[a-z0-9]{8}\]'

# Performs a Shannon entropy analysis on a given block of data.
def shannon(data):
    dic = [0] * 256
    for i in data:
        dic[i] += 1

    hertz = 0
    base = 0.0
    for i in dic:
        if i != 0:
            hertz = i * 1.0 / len(data)
            base += hertz * log(hertz, 2)

    if base < 0.0001 and base > -0.0001:
        return 0

    return base / -8

def uniform_data ( data ):
    char_array = []
    for i in data:
        for j in range( len(i) / 2 ): # each time read one byte
                char_array.append( int( i[j * 2 : j * 2 + 2], 16) )
    return char_array


def extract_read_data_addr( s ):
    p = re.compile( MEM_READ_RE )
    x = p.findall(s)
    r = []
    for item in x:
        #d = int( item.split(':')[0], 16 )
        d = item.split(':')[0]
        a = int( item.split(':')[1].strip('\n')[1:9], 16 )
        r.append( (d, a) ) # record content
    if len(r) > 1:
        raise NameError, s
    return r[0]

def extract_write_data_addr( s ):
    p = re.compile( MEM_WRITE_RE )
    x = p.findall(s)
    r = []
    for item in x:
        #d = int( item.split('=')[1].strip('\n'), 16 )
        d = item.split('=')[1].strip('\n')
        a = int( item.split('=')[0][1:9], 16 )
        r.append( (d, a) ) # record content
    if len(r) > 1:
        raise NameError, s
    return r[0]


def analyzeData( tid, data ):
    memDic = {}
    newData = []
    for s in data:
        s = s.strip("\n")
        if 'R' in s: # is memory read
            (content, addr) = extract_read_data_addr(s) 
            if not addr in memDic:
                newData.append( s + 'I' )
            else:
                newData.append( s + 'T' )
        elif 'W' in s: # is memory write
            (content, addr) = extract_write_data_addr(s)
            memDic[addr] = 1
            newData.append(s)
        else:
            raise NameError, s

    memDic = {}
    for i in range( len(newData) ):
        s = newData[len(newData) - i - 1]
        if 'W' in s: # is memory read
            (content, addr) = extract_write_data_addr(s)
            if not addr in memDic:
                newData[len(newData) - i - 1] += 'O'
                memDic[addr] = 1
            else:
                newData[len(newData) - i - 1] += 'T'

    f = open("../data/rwio" + str(tid)  + ".log", 'w' )
    for s in newData:
        f.write( s + '\n' )
    f.close()
    return newData

def write_dataIO( tid, data ):
    readInDic = {} # 读取输入数据
    readTmpDic = {} # 读取中间数据
    writeOutDic = {} # 写入输出数据
    writeTmpDic = {} # 写入中间数据（后来又被覆盖了）

    for s in data:
        codeAddr = int( s[0:8], 16 )
        if 'R' in s: # is memory read
            (content, addr) = extract_read_data_addr(s)
            if 'I' in s:
                if codeAddr in readInDic:
                    readInDic[codeAddr].append(content)
                else:
                    readInDic[codeAddr] = [content]
            elif 'T' in s:
                if codeAddr in readTmpDic:
                    readTmpDic[codeAddr].append(content)
                else:
                    readTmpDic[codeAddr] = [content]
            else:
                raise NameError, s
        if 'W' in s: # is memory write
            (content, addr) = extract_write_data_addr(s)
            if 'O' in s:
                if codeAddr in writeOutDic:
                    writeOutDic[codeAddr].append(content)
                else:
                    writeOutDic[codeAddr] = [content]
            elif 'T' in s:
                if codeAddr in writeTmpDic:
                    writeTmpDic[codeAddr].append(content)
                else:
                    writeTmpDic[codeAddr] = [content]
            else:
                raise NameError, s
            
    addrList = get_addrlist()

    f = open("../data/instRead" + str(tid)  + ".log", 'w' )
    f.write("#######Read Input Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in readInDic:
            #f.write( "%08x:%d:%s\n"%( addr, len(readDic[addr]), str(readDic[addr]) ) )
            f.write( "%08x:%d,%f\n"%(
                    addr,
                    len( readInDic[addr] ),
                    shannon( uniform_data( readInDic[addr] ) )
                )
            )


    f.write("#######Read Tmp Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in readTmpDic:
            #f.write( "%08x:%d:%s\n"%( addr, len(readDic[addr]), str(readDic[addr]) ) )
            f.write( "%08x:%d\n"%( addr, len( readTmpDic[addr] ) ) )
    f.close()

    f = open("../data/instWrite" + str(tid)  + ".log", 'w' )
    f.write("#######Write Output Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in writeOutDic:
            #f.write( "%08x:%d:%s\n"%( addr, len(writeOutDic[addr]), str(writeOutDic[addr]) ) )
                f.write( "%08x:%d,%f\n"%(
                        addr,
                        len( writeOutDic[addr] ),
                        shannon( uniform_data( writeOutDic[addr] ) )
                    )
                )
    

    f.write("#######Write Tmp Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in writeTmpDic:
            #f.write( "%08x:%d:%s\n"%( addr, len(writeTmpDic[addr]), str(writeTmpDic[addr]) ) )
            f.write( "%08x:%d\n"%(
                    addr,
                    len(writeTmpDic[addr])
                )
            )
    f.close()

    print "Thread %s: IO Analysis Done!"%(tid)

if __name__=="__main__":
    ts = get_threads()
    for t in ts:
        tid = str(t)
        f = open("../data/rw" + tid + ".log", "r")
        data = f.readlines()
        f.close()
        write_dataIO( tid, analyzeData( tid, data ) )

