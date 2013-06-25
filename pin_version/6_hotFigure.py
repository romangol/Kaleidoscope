# -*- coding: utf-8 -*- 
#中文支持

import pylab
import numpy

def draw_all():
    f = open("../data/profiler.log", 'r')
    s_list = f.readlines()
    f.close()

    r_list_x = []
    r_list_y = []
    w_list_x = []
    w_list_y = []

    fig = pylab.figure()
    fig_inst = fig.add_subplot(211)
    fig_mem = fig.add_subplot(212)

    for s in s_list:
        s = s.strip('\n')
        addr = int( s[2:10], 16)
        times = int( s.split('-')[1] )
        if s[0] == 'C':
            r_list_x.append( addr ) # seq num
            r_list_y.append( times ) # addr
        if s[0] != 'C':
            w_list_x.append( addr ) # seq num
            w_list_y.append( times ) # addr
   
    fig_inst.plot( r_list_x, r_list_y, "r." )
    fig_mem.plot( w_list_x, w_list_y, "g." )

    #fig_inst.axis( [0, get_trace_count(), y_min - 1000, y_max + 1000] )
    #fig_mem.axis( [0, get_trace_count(), y_min - 1000, y_max + 1000] )    
    pylab.show() 


if __name__=="__main__":
    draw_all()
