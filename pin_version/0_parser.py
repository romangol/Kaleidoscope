#以二进制的方式读取文件
#coding: UTF-8

import struct

SIZE_OF_MEM_UNIT = 16
SIZE_OF_IP_UNIT = 44

# 去除不必要的字符
def strip_inst( instruction ):
    instruction = instruction.strip('\n')
    instruction = instruction.replace("qword ptr ", "")
    instruction = instruction.replace("dword ptr ", "")
    instruction = instruction.replace("word ptr ", "")
    instruction = instruction.replace("byte ptr ", "")
    instruction = instruction.replace("ptr ", "")
    instruction = instruction.replace("cs:", "")
    instruction = instruction.replace("ds:", "")
    instruction = instruction.replace("es:", "")
    instruction = instruction.replace("fs:", "")
    instruction = instruction.replace("gs:", "")
    instruction = instruction.replace("ss:", "")
    instruction = instruction.replace("0x", "")
    instruction = instruction.replace("rep ", "")
    instruction = instruction.replace("repne ", "")
    return instruction


#将指令pool和trace文件记录的地址对应起来，写回itrace.log
def get_addr_disasm_dict():
    #读取指令pool
    g = open('../data/instPool.out','r')
    insts = g.readlines()
    g.close()

    dic = { 0: "" }
    for s in insts:
        addr, instruction = s.split('|')
        addr = int( addr, 16 )
        dic[addr] = strip_inst( instruction )
    return dic

def get_uid_mem_io_dict():
    #读取io log
    g = open('../data/memTrace.log','r')
    insts = g.readlines()
    g.close()

    dic = {}
    for s in insts:
        content, tid, uid = s.split('|')
        content = content.strip(' ')
        tid = int( tid )
        uid = int( uid.strip('\n') )

        if not tid in dic:
            dic[tid] = {} # 支持线程级别的uid
            
        if uid in dic[tid]:
            if not content in dic[tid][uid]: # pin记录有奇怪的bug会重复记录
                dic[tid][uid] += (';' + content)
        else:
            dic[tid][uid] = content
    return dic

def parseTrace():
    #将trace二进制文件转换为文本格式，并添加上反汇编结果
    f = open('../data/itrace.out','rb')
    g = open('../data/itrace.log','w')

    dic = get_addr_disasm_dict()
    mDic = get_uid_mem_io_dict() # based on memTrace.log!!

    raw = f.read(SIZE_OF_IP_UNIT)
    while raw:
        (addr, threadid, eax, ebx, ecx, edx, edi, esi, ebp, esp, uid) = struct.unpack( "IIIIIIIIIII", raw )
        if uid in mDic[threadid]:
            s = "%08x#%d|%s|%s|%08x, %08x, %08x, %08x, %08x, %08x, %08x, %08x\n"%( addr, threadid, dic[addr], mDic[threadid][uid], eax, ebx, ecx, edx, edi, esi, ebp, esp )
        else:
            s = "%08x#%d|%s||%08x, %08x, %08x, %08x, %08x, %08x, %08x, %08x\n"%( addr, threadid, dic[addr], eax, ebx, ecx, edx, edi, esi, ebp, esp )
        g.write(s)
        raw = f.read(SIZE_OF_IP_UNIT)
    f.close()
    g.close()

    print "Done Trace Parsing!"

def parseMemTrace():
    g = open('../data/memTrace.log', 'w')
    f = open('../data/memTrace.out', 'rb')
    raw = f.read(SIZE_OF_MEM_UNIT)
    while raw:
        (uid, addr, content, ioType, length, threadid) = struct.unpack( "IIIccH", raw )
        length = ord(length)
        if length == 1:
            s = "%c%d@[%08x]=%02x      |%d|%d\n"%( ioType, length, addr, content & 0xFF, threadid, uid )
        if length == 2:
            s = "%c%d@[%08x]=%04x    |%d|%d\n"%( ioType, length, addr, content & 0xFFFF, threadid, uid )
        if length == 4:
            s = "%c%d@[%08x]=%08x|%d|%d\n"%( ioType, length, addr, content, threadid, uid )
        g.write(s)
        raw = f.read(SIZE_OF_MEM_UNIT)
    f.close()
    g.close()

    print "Done Mem parsing!"


if __name__=="__main__":
    parseMemTrace()
    parseTrace()

