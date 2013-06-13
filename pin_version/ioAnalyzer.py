# -*- coding: utf-8 -*- 
# 中文支持

import re

ADDR_RE = '\[[a-z0-9]{8}\]'
REG32_RE = 'e[abcds][xpi]'
REG16_RE = '[abcd]x'
REG8_RE = '[abcd][lh]'

REG_TO_MEM = '\],'
MEM_TO_REG = ',.*\['

def getAddrList():
    f = open("../data/instPool.log")
    d = f.readlines()
    f.close()
    addr = []
    for s in d:
        addr.append( s[0:8] )
    return addr

def getCodeList():
    f = open("../data/instPool.log")
    d = f.readlines()
    f.close()
    code = []
    for s in d:
        code.append( s[9:] )
    return code

def getInput( m_list ):
    mem_dict = {}
    input_dict = {}

    for s in m_list:
        p = re.compile( ADDR_RE )
        x = p.findall(s)
        for i in x:
            addr = int( i[1:9], 16 )
            if "W" in s and addr in mem_dict: # 内存未被使用过的写入仍算输入
                mem_dict[addr] = 1
            elif not (addr in mem_dict): # this is input data
                val = s.split('=')[1].split(':')[0]
                input_dict[addr] = int( val, 16 )
    return input_dict


def getOutput( m_list ):
    mem_dict = {}
    for s in m_list:
        p = re.compile( ADDR_RE + "=[0-9a-f]*" )
        x = p.findall(s)
        for item in x:
            i, j = item.split('=')
            if "W" in s:
                addr = int( i[1:9], 16 )
                mem_dict[addr] = int(j, 16)
    return mem_dict
