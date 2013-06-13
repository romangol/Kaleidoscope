# -*- coding: utf-8 -*- 
# 中文支持

import re

ADDR_RE = '\[[A-Z0-9]{8}\]'
REG_SET = set(["eax", "ebx", "ecx", "edx", "edi", "esi", "ebp", "esp",
               "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl",
               "ax", "bx", "cx", "dx", "si", "di" ])

REG_TYPE = 0
MEM_TYPE = 1
IMM_TYPE = 2

RegDic = { "eax":"", "ebx":"", "ecx":"", "edx":"", "edi":"", "esi":"", "ebp":"", "esp":"",
           "ah":"", "al":"", "bh":"", "bl":"", "ch":"", "cl":"", "dh":"", "dl":"",
           "ax":"", "bx":"", "cx":"", "dx":"", "si":"", "di":"" }

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


def which_type(oprand):
    if oprand in REG_SET:
        return REG_TYPE
    if "[" in oprand:
        return MEM_TYPE
    return IMM_TYPE

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
            return '%s=%s:C|W'%(addr, content )
        else:
            return '%s=%s:%s|W'%(addr, content, oprands )
    if op == 'pop':
        return '%s=%s:%s|R'%(oprands, content, addr)

    if op == 'lea':
        opnum = oprands.split(", ")
        if len(opnum) != 2: raise NameError, code #不是两个操作数的情况
        a, b = opnum
        return '%s=%s'%(a, b[1:-1])

    # 赋值规则
    if "mov" in op:
        if len(op) > 3: # 带条件的mov可能没有mem操作
            if mem == "":
                return " "
        opnum = oprands.split(", ")
        if len(opnum) != 2: raise NameError, code #不是两个操作数的情况
        a, b = opnum
        if which_type(a) == MEM_TYPE  and which_type(b) == REG_TYPE: # [] <-> REG
            return '%s=%s:%s|W'%(addr, content, b)
        elif which_type(a) == MEM_TYPE  and which_type(b) == MEM_TYPE: # REG <-> []
            if mem == "":
                return code
        elif which_type(a) == REG_TYPE  and which_type(b) == MEM_TYPE: # REG <-> []
            if mem == "":
                raise NameError, code
            return '%s=%s:%s|R'%(a, content, addr)
        elif which_type(a) == REG_TYPE  and which_type(b) == REG_TYPE: # REG <-> REG
            return '%s=%s:%s'%(a, regDic[b], b)
        elif which_type(a) == MEM_TYPE  and which_type(b) == IMM_TYPE: # REG <-> REG
            return '%s=%s:C|W'%(addr, b)
        elif which_type(a) == REG_TYPE  and which_type(b) == IMM_TYPE: # REG <-> REG
            return '%s=%s:C'%(a, b)
        else:
            raise NameError, code


    #其余替换内存地址
    if mem != "":
        newCode = addr_replace( code, addr )
    return newCode    

def translate( s_list ):
    g = open("../data/mil.log", 'w')
    
    addr_code_dic = {}
    new_list = []
    for s in s_list:
        addr, code, mem, reg = s.split('|') # split one trace record
        addr = int( addr[0:8], 16 )
        reg = reg.strip('\n')
        addr_code_dic[addr] = code
     
        # translate code to mil
        assign_reg( reg, RegDic )
        if ';' in mem:
            new_code = rewrite_opcode_complex( code, mem, RegDic )
        else:
            new_code = rewrite_opcode( code, mem, RegDic )

        # re arrange a record
        new_list.append( s.split('|')[0] + '|' + new_code )
        g.write( new_list[-1] + '\n' )

    #print addr_opcode_dic
    g.close()
    return new_list


# remove unused instructions
def inst_filter ( lst ):
    new_list = []
    filter_set = set([ "movapd", "movdqa", "leave", "cdq", "ret", "retn", "call", "ret", "std", "cld", "int" ])

    for s in lst:
        if "|j" in s:
            continue
        if "xmm" in s:
            continue
        opcode = s.split('|')[1].split()[0]
        if not (opcode in filter_set):
            new_list.append( s )
    return new_list

if __name__=="__main__":
    f = open("../data/itrace.log")
    s_list = f.readlines()
    f.close()

    # if translate() does not want to parse simple Trace, comment the inst_filter func.
    s_list = inst_filter ( s_list )
    n_list = translate( s_list )
    print "Mil Translated"

    
