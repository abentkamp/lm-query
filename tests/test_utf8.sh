#!/bin/sh
my_dir=`dirname $0`
$my_dir/../bin/lm-query.py $my_dir/data/utf8.arpa < $my_dir/data/utf8.txt
