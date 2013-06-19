del data\w.txt
del data\r.txt
del data\rw.txt
findstr "|W" data\mil.txt > data\w.txt
findstr "|R" data\mil.txt > data\r.txt
findstr "|[RW]" data\mil.txt >> data\rw.txt