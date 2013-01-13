# -*- coding: utf-8 -*- 
#中文支持

import pylab

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


if __name__=="__main__":
    f = open("data\\mil.txt")
    s_list = f.readlines()
    addr_list = []

    for s in s_list:
        # record address and make addr-opcode map        
        inst = s.split('||')
        addr = int(inst[0], 16)
        addr_list.append( int(inst[0], 16) )
    draw_addr(addr_list)

    f.close()
