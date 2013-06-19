# -*- coding: utf-8 -*- 
#中文支持
import re
import pylab

ADDR_RE = '\[[A-Z0-9]{8}\]'

def stat_mem( lst ):
    stat_dict = {}
    for s in lst:
        p = re.compile( ADDR_RE )
        x = p.findall(s)
        for i in x:
            addr = int( i[1:9], 16 )
            if addr in stat_dict:
                stat_dict[addr] = stat_dict[addr] + 1
            else:
                stat_dict[addr] = 1
    for k, v in stat_dict.iteritems():
        print hex(k), v
    return stat_dict


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

def stat_mem_read( m_list ):
    mem_dict = {}
    for s in m_list:
        p = re.compile( ADDR_RE )
        x = p.findall(s)
        for i in x:
            addr = int( i[1:9], 16 )
            if s.find("|W") != -1:
                if addr in mem_dict:
                    mem_dict[addr] += 1
                else:
                    mem_dict[addr] = 1
            else: # memory read
                if addr in mem_dict:
                    print hex(addr), mem_dict[addr]
                else:
                    print hex(addr), "input"



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
    
    draw_map( inst_mem_map )

    f.close()


if __name__=="__main__":
    f = open("data\\w.txt")
    w_list = f.readlines()
    print "Memory Write"
    stat_mem( w_list )
    f.close()


    g = open("data\\r.txt")
    r_list = g.readlines()
    print "Memory Read"
    stat_mem( r_list )
    g.close()


if __name__=="__main__":
    f = open("data\\rw.txt")

    l = f.readlines()
    stat_mem_read( l )
    
    d = get_output( l )

    for k, v in d.iteritems():
        print hex(k), hex(v)
        
    f.close()
