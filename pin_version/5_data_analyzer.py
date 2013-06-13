# -*- coding: utf-8 -*- 
#中文支持

from ioAnalyzer import *

MEM_WRITE_RE = '\[[a-z0-9]{8}\]=[a-z0-9]*'
MEM_READ_RE = '[a-z0-9]*:\[[a-z0-9]{8}\]'

def extract_read_data_addr( s ):
    p = re.compile( MEM_READ_RE )
    x = p.findall(s)
    r = []
    for item in x:
        d = int( item.split(':')[0], 16 )
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
        d = int( item.split('=')[1].strip('\n'), 16 )
        a = int( item.split('=')[0][1:9], 16 )
        r.append( (d, a) ) # record content
    if len(r) > 1:
        raise NameError, s
    return r[0]


def analyzeData( data ):
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

    f = open("../data/rwio.log", 'w' )
    for s in newData:
        f.write( s + '\n' )
    f.close()
    return newData

def write_dataIO( data ):
    readInDic = {} # 读取输入数据
    readTmpDic = {} # 读取中间数据
    writeOutDic = {} # 写入输出数据
    writeTmpDic = {} # 写入中间数据（后来又被覆盖了）

    for s in data:
        codeAddr = int( s[0:8], 16 )
        if 'R' in s: # is memory read
            (content, addr) = extract_read_data_addr(s)
            if s[-1] == 'I':
                if codeAddr in readInDic:
                    readInDic[codeAddr].append(content)
                else:
                    readInDic[codeAddr] = [content]
            elif s[-1] == 'T':
                if codeAddr in readTmpDic:
                    readTmpDic[codeAddr].append(content)
                else:
                    readTmpDic[codeAddr] = [content]
            else:
                raise NameError, s
        if 'W' in s: # is memory write
            (content, addr) = extract_write_data_addr(s)
            if s[-1] == 'O':
                if codeAddr in writeOutDic:
                    writeOutDic[codeAddr].append(content)
                else:
                    writeOutDic[codeAddr] = [content]
            elif s[-1] == 'T':
                if codeAddr in writeTmpDic:
                    writeTmpDic[codeAddr].append(content)
                else:
                    writeTmpDic[codeAddr] = [content]
            else:
                raise NameError, s
            
    addrList = getAddrList()

    f = open("../data/instRead.log", 'w' )
    f.write("#######Read Input Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in readInDic:
            #f.write( "%08x:%d:%s\n"%( addr, len(readDic[addr]), str(readDic[addr]) ) )
            f.write( "%08x:%d\n"%( addr, len( readInDic[addr] ) ) )

    f.write("#######Read Tmp Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in readTmpDic:
            #f.write( "%08x:%d:%s\n"%( addr, len(readDic[addr]), str(readDic[addr]) ) )
            f.write( "%08x:%d\n"%( addr, len( readTmpDic[addr] ) ) )
    f.close()

    f = open("../data/instWrite.log", 'w' )
    f.write("#######Write Output Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in writeOutDic:
            f.write( "%08x:%d:%s\n"%( addr, len(writeOutDic[addr]), str(writeOutDic[addr]) ) )
            #f.write( "%08x:%d\n"%( addr, len(writeOutDic[addr]) ) )
    f.write("#######Write Tmp Data#######\n")
    for a in addrList:
        addr = int(a, 16)
        if addr in writeTmpDic:
            f.write( "%08x:%d:%s\n"%( addr, len(writeTmpDic[addr]), str(writeTmpDic[addr]) ) )
            #f.write( "%08x:%d\n"%( addr, len(writeTmpDic[addr]) ) )
    f.close()



if __name__=="__main__":
    f = open("../data/rw.log")
    data = f.readlines()
    f.close()

    write_dataIO( analyzeData( data ) )

    print "IO Analysis Done!"
