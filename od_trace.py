# -*- coding: utf-8 -*- 
# 中文支持

import re

ADDR_RE = '\[[A-Z0-9]{8}\]'
REG32_RE = 'E[ABCDS][XPI]'
REG16_RE = '[ABCD]X'
REG8_RE = '[ABCD][LH]'

REG_TO_MEM = '\],'
MEM_TO_REG = ',.*\['

REG_SET = set(["EAX", "EBX", "ECX", "EDX", "EDI", "ESI", "EBP", "ESP", "AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL", "AX", "BX", "CX", "DX"])


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

# remove unused instructions
def inst_filter ( lst ):
    g = open("data\\trace.txt", 'w')
    new_list = []
    filter_set = set([ "LEAVE", "CDQ", "RET", "RETN", "CALL", "RET", "STD", "CLD" ])

    counter = 0
    for s in lst:
        counter += 1
        if s.find("\tJ") != -1:
            continue
        if s.find("\tREP") != -1:
            continue
        try:
            opcode = s.split('\t')[1].split()[0]
        except:
            print s
            break;
        if not (opcode in filter_set):
            new_list.append( s.strip('\n') + ' #%d\n'%(counter) )
            g.write( s.strip('\n') + ' #%d\n'%(counter) )
    g.close()
    return new_list

# replace [name] as [addr]
def addr_replace ( opcode, addr ):
    prefix = opcode[ :opcode.find('[')]
    postfix = opcode[ opcode.find(']') + 1: ] 
    return prefix + addr + postfix


def rewrite_opcode( opcode, m_dic, r_dic ):
    ops = opcode.split()
    op = ops[0]
    if opcode.find(',') != -1:
        opnum = ops[1].split(',')
        if opnum[0].find('[') != -1  and opnum[1] in REG_SET: # [] <-> REG
            if op == 'MOV': return '%s=%s:%s|W'%(m_dic[0], m_dic[1], opnum[1])
            #if op == 'TEST': return 'TEST=%s:%s|R'%(m_dic[1], m_dic[0])
        if opnum[1].find('[') != -1  and opnum[0] in REG_SET: # REG <-> []
            if op == 'MOV': return '%s=%s:%s|R'%(opnum[0], m_dic[1], m_dic[0])
            if op == 'MOVZX': return '%s=%s:%s|R'%(opnum[0], m_dic[1], m_dic[0])
            #if op == 'TEST': return 'TEST=%s:%s|R'%(m_dic[1], m_dic[0])
        if opnum[1] in REG_SET and opnum[0] in REG_SET: # REG <-> REG
            if op == 'MOV': return '%s=:%s|'%(opnum[0], opnum[1])

    try:
        opnum = ops[1]
    except:
        print opcode
        return ""
    # 特殊指令指定规则
    if op == 'PUSH': return '%s=%s:%s|W'%(m_dic[0], m_dic[1], opnum[0])
    if op == 'POP': return '%s=%s:%s|R'%(opnum[0], m_dic[1], m_dic[0])
         

    #其余替换内存地址
    if m_dic:
        opcode = addr_replace( opcode, m_dic[0] )
    return opcode    

def translate( s_list ):
    g = open("data\\mil.txt", 'w')
    
    addr_opcode_dic = {}
    new_list = []
    for s in s_list:
        # record address and make addr-opcode map        
        inst = s.strip('\n').split('\t')
        addr = int(inst[0], 16)
        addr_opcode_dic[addr] = inst[1]

        # translate opcode to mil
        new_op = rewrite_opcode( inst[1], get_mem_map(s), get_reg_map(s) )
        new_op = inst[0] + '||' + new_op
        new_op += ' #' + s.split('#')[1]
        new_list.append(new_op)
        g.write( new_op )

    #print addr_opcode_dic
    g.close()
    return new_list

if __name__=="__main__":
    f = open("data\\od_trace.txt")

    s_list = f.readlines()
    s_list = inst_filter ( s_list )

    print "count:", len(s_list)
    
    n_list = translate( s_list )


    f.close()
