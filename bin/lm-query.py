#!/usr/bin/env python2.7
import kenlm
import fileinput
import argparse
import sys

parser = argparse.ArgumentParser(description='Process some integers.', usage ='%(prog)s arpa_file < test_data > probabilities 2> perplexity')
parser.add_argument('arpa_file', metavar='arpa_file', help='bla')

parser.add_argument('test_data', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
parser.add_argument('probabilities', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
parser.add_argument('perplexity', nargs='?', type=argparse.FileType('w'), default=sys.stderr)

args = parser.parse_args()

model = kenlm.LanguageModel(args.arpa_file)

for sentence in args.test_data:
    print(model.score(sentence))
