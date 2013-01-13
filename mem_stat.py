# -*- coding: utf-8 -*- 
#中文支持
import re

ADDR_RE = '\[[A-Z0-9]{8}\]'

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


if __name__=="__main__":
    f = open("data\\rw.txt")

    l = f.readlines()
    stat_mem_read( l )
    
    d = get_output( l )

    for k, v in d.iteritems():
        print hex(k), hex(v)
        
    f.close()

