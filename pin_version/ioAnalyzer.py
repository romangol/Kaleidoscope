# -*- coding: utf-8 -*- 
# 中文支持

import re

ADDR_RE = '\[[a-z0-9]{8}\]'
REG32_RE = 'e[abcds][xpi]'
REG16_RE = '[abcd]x'
REG8_RE = '[abcd][lh]'

REG_TO_MEM = '\],'
MEM_TO_REG = ',.*\['


REG_SET = set(["eax", "ebx", "ecx", "edx", "edi", "esi", "ebp", "esp",
               "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl",
               "ax", "bx", "cx", "dx", "si", "di", "bp" ])


REG_TYPE = 0
MEM_TYPE = 1
IMM_TYPE = 2
REG_OP_TYPE = 3

def get_threads():
    f = open("../data/threads.out",'r')
    ls = f.readline()
    f.close()

    s = ls.split()
    t = []

    for i in s:
        t.append( int(i) )
    return t

def get_addrlist():
    f = open("../data/instPool.log")
    d = f.readlines()
    f.close()
    addr = []
    for s in d:
        addr.append( s[0:8] )
    return addr

def get_codelist():
    f = open("../data/instPool.log")
    d = f.readlines()
    f.close()
    code = []
    for s in d:
        code.append( s[9:] )
    return code

def get_input( m_list ):
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


def get_output( m_list ):
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


def which_type(oprand):
    if oprand in REG_SET:
        return REG_TYPE
    if "[" in oprand:
        return MEM_TYPE
    for i in REG_SET:
        if i in oprand:
            return REG_OP_TYPE
    return IMM_TYPE
