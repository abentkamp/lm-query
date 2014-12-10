#!/usr/bin/env python2.7
import argparse
import sys
import math
from arpaparser import ArpaParser 

def parseArguments():
    # TODO: add help texts
    parser = argparse.ArgumentParser(description='Process some integers.', usage ='%(prog)s arpa_file < test_data > probabilities 2> perplexity')
    parser.add_argument('arpa_file', metavar='arpa_file', type=argparse.FileType('r'), help='bla')

    parser.add_argument('test_data', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('probabilities', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('perplexity', nargs='?', type=argparse.FileType('w'), default=sys.stderr)

    return parser.parse_args()


args = parseArguments()

arpaParse = ArpaParser(args.arpa_file)
print arpaParse.ngramLogProbs

def calculateProp(ngram, arpaParse):
    ngramString = ' '.join(ngram)
    if ngramString in arpaParse.ngramLogProbs[len(ngram)]:
        return arpaParse.ngramLogProbs[len(ngram)][ngramString]
    elif len(ngram) == 1:
        return arpaParse.ngramLogProbs[1]['<unk>']
    else:
        historyString = ' '.join(ngram[:-1])
        if historyString in arpaParse.ngramBackoffs[len(ngram)-1]:
            return arpaParse.ngramBackoffs[len(ngram)-1][historyString] + calculateProp(ngram[1:], arpaParse)
        else:
            return calculateProp(ngram[1:], arpaParse)


# TODO: support UTF8 encoding
totalLogProb = 0
wordCount = 0
for sentence in args.test_data:
    sentence = sentence.strip()
    history = ['<s>']
    wordList = sentence.split(' ');
    wordList.append('</s>')
    sentenceTotalLogProb = 0
    for word in wordList:
        history.append(word)
        if len(history) not in arpaParse.ngramLogProbs:
            history.pop(0)

        wordLogProb = calculateProp(history, arpaParse)
        sentenceTotalLogProb += wordLogProb
        wordCount += 1

        print word
        print wordLogProb

    totalLogProb += sentenceTotalLogProb

    print 'Sentence Total:'
    print sentenceTotalLogProb

perplexity = math.pow(10, -totalLogProb/wordCount)
print 'PP'
print perplexity

