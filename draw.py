# -*- coding: utf-8 -*- 
#中文支持

import pylab
import numpy

def get_trace_count():
    f = open("data\\od_trace.txt")
    c = len( f.readlines() )
    f.close()
    return c

def draw_inst():
    f = open("data\\mil.txt")
    s_list = f.readlines()
    f.close()

    y_min = 0x80000000
    y_max = 0
    X = []
    Y = []
    for s in s_list:
        X.append( int( s.strip('\n').split('#')[1] ) ) # seq num
        Y.append( int(s.split('||')[0], 16) ) # addr
        if i > y_max: y_max = i
        if i < y_min: y_min = i

    pylab.plot( X, Y )
    pylab.axis( [0, get_trace_count(), y_min - 1000, y_max + 1000] )
    pylab.show() 


def draw_all( type ):
    f = open("data\\mil.txt")
    s_list = f.readlines()
    f.close()

    y_min = 0x80000000
    y_max = 0
    X = []
    Y = []
    for s in s_list:
        addr = int(s.split('||')[0], 16)
        X.append( int( s.strip('\n').split('#')[1] ) ) # seq num
        Y.append( addr ) # addr
        if addr > y_max: y_max = addr
        if addr < y_min: y_min = addr

    fig = pylab.figure()
    fig_inst = fig.add_subplot(211)
    fig_mem = fig.add_subplot(212)
    fig_inst.plot( X, Y, "g" )
    fig_inst.axis( [0, get_trace_count(), y_min - 1000, y_max + 1000] )


    f = open("data\\io.txt")
    s_list = f.readlines()
    f.close()

    r_list_x = []
    r_list_y = []
    w_list_x = []
    w_list_y = []

    for s in s_list:
        pos = s.find('[')
        addr = int( s[pos+1:pos+9], 16 )
        if addr > y_max: y_max = addr
        if addr < y_min: y_min = addr 
        if s.find('|R') != -1:
            r_list_y.append( addr )
            r_list_x.append( int( s.strip('\n').split('#')[1] ) ) #read counter
        if s.find('|W') != -1:
            w_list_y.append( int( addr ) )
            w_list_x.append( int( s.strip('\n').split('#')[1] ) ) #read counter

    if type == 'W':
        fig_mem.plot( w_list_x, w_list_y, "r." )
    if type == 'R':
        fig_mem.plot( r_list_x, r_list_y, "r." )

    fig_mem.axis( [0, get_trace_count(), y_min - 1000, y_max + 1000] )    
    pylab.show() 

def draw_io( type ):
    f = open("data\\io.txt")
    s_list = f.readlines()
    f.close()

    r_list_x = []
    r_list_y = []
    w_list_x = []
    w_list_y = []

    y_min = 0x80000000
    y_max = 0

    for s in s_list:
        pos = s.find('[')
        addr = int( s[pos+1:pos+9], 16 )
        if addr > y_max: y_max = addr
        if addr < y_min: y_min = addr 
        if s.find('|R') != -1:
            r_list_y.append( addr )
            r_list_x.append( int( s.strip('\n').split('#')[1] ) ) #read counter
        if s.find('|W') != -1:
            w_list_y.append( int( addr ) )
            w_list_x.append( int( s.strip('\n').split('#')[1] ) ) #read counter

    if type == 'W': pylab.plot( w_list_x, w_list_y, "ro" )
    if type == 'R': pylab.plot( r_list_x, r_list_y, "ro" )

    pylab.axis( [0, get_trace_count(), y_min - 1000, y_max + 1000] )
    pylab.show()





if __name__=="__main__":
    draw_all( 'W' )
