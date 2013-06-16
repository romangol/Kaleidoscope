#以二进制的方式读取文件
#coding: UTF-8

def test():
    f = open('base.txt','r')
    data = f.readlines()
    f.close()

    basicAddr = []
    for s in data:
        basicAddr.append( int(s[2:10], 16) )
    basicSet = set(basicAddr)
    
    f = open('test.txt','r')
    data = f.readlines()
    f.close()

    f = open('result.txt','w')
    for s in data:
        if int(s[2:10], 16) in basicSet:
            f.write(s)
    f.close()
        
    
if __name__=="__main__":
    test()

