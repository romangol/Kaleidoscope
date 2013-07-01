# -*- coding: utf-8 -*- 
# 中文支持

import re
from ioAnalyzer import *

ADDR_RE = '\[[A-Z0-9]{8}\]'
REG_SET = set(["eax", "ebx", "ecx", "edx", "edi", "esi", "ebp", "esp",
               "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl",
               "ax", "bx", "cx", "dx", "si", "di", "bp" ])


RegDic = { "eax":"", "ebx":"", "ecx":"", "edx":"", "edi":"", "esi":"", "ebp":"", "esp":"",
           "ah":"", "al":"", "bh":"", "bl":"", "ch":"", "cl":"", "dh":"", "dl":"",
           "ax":"", "bx":"", "cx":"", "dx":"", "si":"", "di":"", "bp":"" }

def assign_reg( r, regDic ):
    d = r.split(", ")
    regDic["eax"] = d[0]
    regDic["ebx"] = d[1]
    regDic["ecx"] = d[2]
    regDic["edx"] = d[3]
    regDic["edi"] = d[4]
    regDic["esi"] = d[5]
    regDic["ebp"] = d[6]
    regDic["esp"] = d[7]
    regDic["ah"] = d[0][4:6]
    regDic["al"] = d[0][6:8]
    regDic["bh"] = d[1][4:6]
    regDic["bl"] = d[1][6:8]
    regDic["ch"] = d[2][4:6]
    regDic["cl"] = d[2][6:8]
    regDic["dh"] = d[3][4:6]
    regDic["dl"] = d[3][6:8]
    regDic["ax"] = d[0][4:8]
    regDic["bx"] = d[1][4:8]
    regDic["cx"] = d[2][4:8]
    regDic["dx"] = d[3][4:8]
    regDic["si"] = d[5][4:8]
    regDic["di"] = d[4][4:8]

# replace [name] as [addr]
def addr_replace ( opcode, addr ):
    prefix = opcode[ :opcode.find('[')]
    postfix = opcode[ opcode.find(']') + 1: ] 
    return prefix + addr + postfix

# remove unused instructions
def inst_filter ( s ):
    if "|j" in s or "xmm" in s:
        return True

    filter_set = set([ "movapd", "movdqa", "leave", "cdq", "ret", "retn", "call", "ret", "std", "cld", "int" ])
    opcode = s.split('|')[1].split()[0]
    if not (opcode in filter_set):
        return False
    return True

def rewrite_opcode_complex( code, mem, regDic ):
    op = code.split()[0]

    memA, memB = mem.split(';')

    if 'R' in memA and 'W' in memB:
        addrA, contentA = memA[3:].split('=')
        addrB, contentB = memB[3:].split('=')
    elif 'R' in memB and 'W' in memA:
        addrA, contentA = memB[3:].split('=')
        addrB, contentB = memA[3:].split('=')
    elif 'R' in memB and 'R' in memA:
        print code, mem
        addrA, contentA = memA[3:].split('=')
        addrB, contentB = memB[3:].split('=')
        #return '%s:%s %s:%s|R'%(addrA, contentA, addrB, contentB )
        return ""
    else:
        raise NameError, code

    return '%s=%s:%s|W'%(addrA, contentB, addrB )

def rewrite_opcode( code, mem, regDic ):
    newCode = code
    op = code.split()[0]
    oprands = code[code.index(' ') + 1:]

    if mem != "":
        addr, content = mem[3:].split('=')
        content = content.strip(' ')
    
    # 特殊指令指定规则
    if op == 'push':
        if which_type(oprands) == IMM_TYPE:
            return '%s=%s:IMM-%s|W'%(addr, content, content )
        else:
            return '%s=%s:%s|W'%(addr, content, oprands )
    if op == 'pop':
        return '%s=%s:%s|R'%(oprands, content, addr)

    if op == 'lea':
        opnum = oprands.split(", ")
        if len(opnum) != 2: raise NameError, code #不是两个操作数的情况
        a, b = opnum
        return '%s=%s'%(a, b[1:-1])
    if op == 'imul':
        opnum = oprands.split(", ")
        if len(opnum) != 3: raise NameError, code #不是三个操作数的情况
        return '%s=%s*%s'%(opnum[0], opnum[1], opnum[2])
        

    # 赋值规则
    if "mov" in op:
        if len(op) > 3 and mem == "":
            return " " # 带条件的mov可能没有mem操作
        elif op == "movsd":
            return '[%s]=%s:[%s]|W'%(regDic["esi"], content, regDic["edi"])

        opnum = oprands.split(", ")
        if len(opnum) != 2: raise NameError, code #不是两个操作数的情况
        a, b = opnum
        if which_type(a) == MEM_TYPE  and which_type(b) == REG_TYPE: # [] <-> REG
            return '%s=%s:%s|W'%(addr, content, b)
        elif which_type(a) == MEM_TYPE  and which_type(b) == MEM_TYPE: # REG <-> []
            if mem == "": return code
        elif which_type(a) == REG_TYPE  and which_type(b) == MEM_TYPE: # REG <-> []
            if mem == "":
                raise NameError, code
            return '%s=%s:%s|R'%(a, content, addr)
        elif which_type(a) == REG_TYPE  and which_type(b) == REG_TYPE: # REG <-> REG
            return '%s=%s:%s'%(a, regDic[b], b)
        elif which_type(a) == MEM_TYPE  and which_type(b) == IMM_TYPE: # REG <-> REG
            return '%s=%s:IMM-%s|W'%(addr, b, b)
        elif which_type(a) == REG_TYPE  and which_type(b) == IMM_TYPE: # REG <-> REG
            return '%s=%s:IMM-%s'%(a, b, b)
        else:
            raise NameError, code


    #其余替换内存地址
    if mem != "":
        newCode = addr_replace( code, addr )
    return newCode    

def translate( tid ):
    addr_code_dic = {}

    f = open("../data/itrace" + str(tid) + ".log", "r")
    g = open("../data/mil" + str(tid) + ".log", 'w')

    s = f.readline()
    while s != "":
        if inst_filter(s) == False:
            addr, code, mem, reg = s.split('|') # split one trace record
            addr = int( addr[0:8], 16 )
            reg = reg.strip('\n')
            addr_code_dic[addr] = code
         
            # translate code to mil
            assign_reg( reg, RegDic )
            if ';' in mem: # more than one mem operation
                new_code = rewrite_opcode_complex( code, mem, RegDic )
            else:
                new_code = rewrite_opcode( code, mem, RegDic )

            # re arrange a record
            if new_code != " ":
                g.write( s.split('|')[0] + '|' + new_code + '\n' )
        s = f.readline()

    #print addr_opcode_dic
    g.close()
    f.close()

    print "Thread %d: MIL translated\n"%(tid)




if __name__=="__main__":
    ts = get_threads()
    for t in ts:
        translate( t )
    
