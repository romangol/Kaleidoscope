# -*- coding: utf-8 -*- 
# 中文支持

import re
import pylab
import get_io

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
    f = open("../data/rw.log")
    insts = f.readlines()
    in_dic = get_io.get_input( insts )
    out_dic = get_io.get_output( insts )
    f.close()
    
    f = open("../data/mil.log")
    s_list = f.readlines()
    f.close()
    
    reg_set = set(["eax", "ebx", "ecx", "edx", "edi", "esi", "ebp", "esp", "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl", "ax", "bx", "cx", "dx"])
    regDic = { "eax":"", "ebx":"", "ecx":"", "edx":"", "edi":"", "esi":"", "ebp":"", "esp":"",
           "ah":"", "al":"", "bh":"", "bl":"", "ch":"", "cl":"", "dh":"", "dl":"",
           "ax":"", "bx":"", "cx":"", "dx":"" }
    addr_map = {}

    for s in s_list:
        s = s[9:] # remove the addr at the beginning.

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
    
