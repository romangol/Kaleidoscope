# -*- coding: utf-8 -*- 
#中文支持

import pylab


def draw_map( im_map ):
    X = []
    Y = []
    for k, v in im_map.iteritems():
        X.append(k)
        Y.append(v)
    pylab.plot( X, Y, "r*" )
    pylab.show() 


if __name__=="__main__":
    f = open("data\\r.txt")
    s_list = f.readlines()

    inst_mem_map = {}

    for s in s_list:
        # record address and make addr-opcode map        
        inst = s.split("||")
        addr = int(inst[0], 16)
        if addr in inst_mem_map:
            inst_mem_map[addr] += 1
        else:
            inst_mem_map[addr] = 1

    for k, v in inst_mem_map.iteritems():
        print hex(k), hex(v)
    
    #draw_map( inst_mem_map )

    f.close()
