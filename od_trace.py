# -*- coding: utf-8 -*- 
#中文支持

import pylab
import re

ADDR_RE = '\[[A-Z0-9]{8}\]'
REG32_RE = 'E[ABCDS][XPI]'
REG16_RE = '[ABCD]X'
REG8_RE = '[ABCD][LH]'

REG_TO_MEM = '\],'
MEM_TO_REG = ',.*\['


def draw_addr( addr_list ):
    X = []
    Y = []
    counter = 0
    for i in addr_list:
        X.append(counter)
        Y.append(i)
        counter = counter + 1
    pylab.plot( X, Y )
    pylab.show() 

def rewrite_opcode( opcode, m_dic, r_dic ):
    ops = opcode.split()
    op = ops[0]
    if len(ops) > 1:
        opnum = ops[1].split(',')
    
    if op == 'PUSH':
        return '%s=%s:%s|W'%(m_dic[0], m_dic[1], opnum[0])
    if op == 'POP':
        return '%s=%s:%s|R'%(opnum[0], m_dic[1], m_dic[0])
    if op == 'MOV':
        if re.search ( REG_TO_MEM, ops[1] ):
            new_op = '%s=%s:%s|W'%(m_dic[0], m_dic[1], opnum[1])
            return new_op
        if re.search ( MEM_TO_REG, ops[1] ):
            #print ops[1]
            new_op = '%s=%s:%s|R'%(opnum[0], m_dic[1], m_dic[0])
            return new_op
        return '%s=%s:%s'%(opnum[0], r_dic[1], opnum[1])
    if op == 'MOVZX':
        if re.search ( MEM_TO_REG, ops[1] ):
            new_op = '%s=000000%s:%s|R'%(m_dic[0], m_dic[1], opnum[1])
            return new_op
        print ops[1]
        return '%s=000000%s:%s'%(opnum[0], r_dic[1], opnum[1])
    return opcode    

# transform [xxxx]=xx or REG=xx as map [xxxx]:xx
def get_mem_map( inst ):
    d = []
    p = re.compile( ADDR_RE + '=[0-9A-F]*' )
    x = p.findall(inst)
    for i in x:
        val = i.split('=')
        d.append( val[0] )
        d.append( val[1] )
    return d

def get_reg_map( inst ):
    d = []
    p = re.compile( REG32_RE + '=[0-9A-F]{8}' )
    x = p.findall(inst)
    for i in x:
        val = i.split('=')
        d.append( val[0] )
        d.append( val[1] )
    return d


if __name__=="__main__":
    f = open("data\\trace.txt")
    s_list = f.readlines()
    
    addr_list = []
    opcode_list = []

    addr_opcode_dic = {}
    reg_dic = {}
    mem_dic = {}

    for s in s_list:
        # record address and make addr-opcode map        
        inst = s.strip('\n').split('\t')
        addr = int(inst[0], 16)
        addr_list.append( int(inst[0], 16) )
        addr_opcode_dic[addr] = inst[1]

        # translate opcode to mil

        m = get_mem_map(s)
        r = get_reg_map(s)
        new_op = rewrite_opcode( inst[1], m, r )
        opcode_list.append( new_op )
    #draw_addr(addr_list)
    #print addr_list
    #print addr_opcode_dic

    g = open("data\\mil.txt", 'w')
    for i in opcode_list:
        g.write(i)
        g.write('\n')
    g.close()

    f.close()
