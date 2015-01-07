#!/bin/sh
my_dir=`dirname $0`
$my_dir/../bin/lm-query.py $my_dir/data/simple.arpa < $my_dir/data/simple.txt

