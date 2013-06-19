# -*- coding: utf-8 -*- 
# 中文支持

import re
import pylab

ADDR_RE = '\[[A-Z0-9]{8}\]'
REG32_RE = 'E[ABCDS][XPI]'
REG16_RE = '[ABCD]X'
REG8_RE = '[ABCD][LH]'

REG_TO_MEM = '\],'
MEM_TO_REG = ',.*\['


def get_output( m_list ):
    mem_dict = {}
    for s in m_list:
        p = re.compile( ADDR_RE + "=[0-9A-F]*" )
        x = p.findall(s)
        for item in x:
            i, j = item.split('=')
            if s.find("|W") != -1:
                addr = int( i[1:9], 16 )
                try:
                    mem_dict[addr] = int(j, 16)
                except:
                    print s
                    break
    return mem_dict

def get_input( m_list ):
    mem_dict = {}
    input_dict = {}
    for s in m_list:
        p = re.compile( ADDR_RE )
        x = p.findall(s)
        for i in x:
            addr = int( i[1:9], 16 )
            if s.find("|W") != -1:
                mem_dict[addr] = 1
            else:
                if not (addr in mem_dict): # this is input data
                    try:
                        val = s.split('=')[1].split(':')[0]
                    except:
                        print s
                        break
                    input_dict[addr] = int( val, 16 )
    return input_dict




def reg_extend( r ):
    if len(r) == 2:
        return "E" + r[0] + "X"
    return r

def fill_splitter( s ):
    if s != "" and s[len(s) - 1] != '|':
        s += '|'
    return s


def draw_bar_plot(X, Y):
    pylab.plot(X, Y, "g.")
    #pylab.ylim(-1.25,+1.25)
    pylab.show()

if __name__=="__main__":
    f = open("data/rw.txt")
    insts = f.readlines()
    in_dic = get_input( insts )
    out_dic = get_output( insts )
    f.close()
    
    f = open("data\\mil.txt")

    reg_set = set(["EAX", "EBX", "ECX", "EDX", "EDI", "ESI", "EBP", "ESP", "AH", "AL", "BH", "BL", "CH", "CL", "DH", "DL", "AX", "BX", "CX", "DX"])
    reg_map = {}
    for i in reg_set:
        reg_map[i] = ""
    addr_map = {}

    s_list = f.readlines()
    for s in s_list:
        s = s.split("||")[1] # remove address!
        if s.find(':') != -1: # assign operation
            src = s.split(':')[1].split('|')[0]
            dest = s.split('=')[0]

            if re.match( ADDR_RE, dest ):
                if src in reg_set:  #[xxxxxxxx]=REG
                    src = reg_extend(src)
                    addr = int ( dest[1:9], 16 )
                    if not (addr in addr_map):
                        addr_map[addr] = ""
                    addr_map[addr] += reg_map[src]
                    addr_map[addr] = fill_splitter( addr_map[addr] )

            if re.match( ADDR_RE, src ):
                if dest in reg_set: #REG=[xxxxxxxx]
                    dest = reg_extend(dest)
                    if src in addr_map: # the address is used at least once
                        reg_map[dest] = addr_map[src] # closure passing
                    else:
                        if int(src[1:9], 16) in in_dic:
                            reg_map[dest] = src
                    reg_map[dest] = fill_splitter( reg_map[dest] )

        else: # arithmetic and compare operation
            if s.find(',') != -1:
                op = s.split()[0]
                src = s.split()[1].split(',')[0]
                dest = s.split()[1].split(',')[1]
                if src in reg_set:
                    src = reg_extend(src)
                    if dest in reg_set:
                        dest = reg_extend(dest)
                        if op.find('MOV'):
                            reg_map[src] = reg_map[dest] #assign
                        else:
                            reg_map[src] += reg_map[dest] # closure passing
                    reg_map[src] = fill_splitter( reg_map[src] )
                    # add operation?
                    reg_map[src] += op
                    reg_map[src] = fill_splitter( reg_map[src] )

    f.close()


    X = []
    Y = []

    for k,v in  addr_map.iteritems():
        res = v.split('|')
        res = set(res)
        if len(res) > 1:
            X.append(k)
            Y.append( len(res) )
            #if len(res) > 100: print k, res

    draw_bar_plot( X, Y )    
    
