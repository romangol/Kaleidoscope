findstr /v "JMP" data\od_trace.txt > 1.txt
findstr /v "CALL" 1.txt > 2.txt
findstr /v "RET" 2.txt > 1.txt
findstr /v "CMP" 1.txt > 2.txt
findstr /v "TEST" 2.txt > 1.txt
findstr /v "REP" 1.txt > 2.txt
findstr /r /v "\<J..\>" 2.txt > 1.txt
findstr /r /v "\<J.\>" 1.txt > data\trace.txt
del 1.txt
del 2.txt
