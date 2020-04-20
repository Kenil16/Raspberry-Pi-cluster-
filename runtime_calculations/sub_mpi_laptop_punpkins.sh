#!/bin/bash

p=4

start_=`date +%s%3N`
python big_data_processing.py
end_=`date +%s%3N`

runtime=$((end_ - start_))
text="laptop $runtime $p"

echo $text >> runtime_pumpkins_history.txt
echo $runtime
