# -*- coding: utf-8 -*- 
#中文支持
import re

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

