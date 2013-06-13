python 0_parser.py
python 1_translate.py
findstr "|[RW]" ..\data\mil.log > ..\data\rw.log
sort ../data/instPool.out > ../data/instPool1.log
uniq ../data/instPool1.log > ../data/instPool.log
del ..\data\instPool1.log
python 4_data_analyzer.py