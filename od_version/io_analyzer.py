# -*- coding: utf-8 -*- 
#中文支持
import re

ADDR_RE = '\[[A-Z0-9]{8}\]'


def get_output( m_list ):
    mem_dict = {}
    write_dic = {}
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
                write_dic[addr] = s

    g = open("data/io.txt", "a")
    for k, v in write_dic.iteritems():
        g.write(v)
    g.close()

    return mem_dict

def get_input( m_list ):
    g = open("data/io.txt", "w")
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
                    val = s.split('=')[1].split(':')[0]
                    input_dict[addr] = int( val, 16 )
                    g.write(s)
    g.close()
    return input_dict

if __name__=="__main__":
    f = open("data/rw.txt")
    insts = f.readlines()
    f.close()

    in_dic = get_input( insts )
    out_dic = get_output( insts )

    g = open("data/io_data.txt", "w")
    g.write("input data len: %d\n"%( len(in_dic) ) )
    for k, v in in_dic.iteritems():
        g.write( "%08x-%02x\n"%(k,v) )
    g.write("#########\n")

    g.write( "output data len: %d\n"%( len(out_dic) ) )
    for k, v in out_dic.iteritems():
        g.write( "%08x-%02x\n"%(k,v) )
    g.close()

