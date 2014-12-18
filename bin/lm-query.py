#!/usr/bin/env python2.7
import argparse
import sys
import math
import re

def main():

    args = parseArguments()
    print args.arpa_file.encoding

    arpaParse = parseArpa(args.arpa_file)
    print arpaParse['ngramLogProbs']

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
            if len(history) not in arpaParse['ngramLogProbs']:
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

def parseArguments():
    # TODO: add help texts
    parser = argparse.ArgumentParser(description='Process some integers.', usage ='%(prog)s arpa_file < test_data > probabilities 2> perplexity')
    parser.add_argument('arpa_file', metavar='arpa_file', type=argparse.FileType('r'), help='bla')

    parser.add_argument('test_data', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('probabilities', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    parser.add_argument('perplexity', nargs='?', type=argparse.FileType('w'), default=sys.stderr)

    return parser.parse_args()

def parseArpa(arpaFile):
    # These variables will be returned in the end:
    ngramCounts = {}
    ngramBackoffs = {}
    ngramLogProbs = {}

    # These variables hold the state of the parser:
    beforeData = True # True if we are before the \data\ keyword in the file
    ngramOrder = None # The current order of n-grams
    lineNumber = 0 # The current line number in the file

    # Go to the start of the file
    arpaFile.seek(0)

    # Iterate over the lines of the file:
    for line in arpaFile:
        lineNumber += 1

        if beforeData: 
            if line.strip() == '\\data\\':
                beforeData = False
        else:
            ngramCountRegex = re.match('^ngram (\d+)=(\d+)$',line)
            listKeywordRegex = re.match('^\\\\(\d+)-grams:$',line)
            if ngramOrder != None:
                listItemRegex = re.match('^(-?\d+(\.\d+)?)\s+' + '(\S+' + (' \S+' * (ngramOrder-1)) + ')' + '\s+(-?\d+(\.\d+)?)?$',line)
            if ngramCountRegex != None:
                ngramOrder = int(ngramCountRegex.group(1))
                ngramCount = int(ngramCountRegex.group(2))
                ngramCounts[ngramOrder] = ngramCount
            elif listKeywordRegex != None:
                ngramOrder = int(listKeywordRegex.group(1))
                ngramLogProbs[ngramOrder] = {}
                ngramBackoffs[ngramOrder] = {}
            elif ngramOrder != None and listItemRegex != None:
                ngramLogProb = float(listItemRegex.group(1))
                words = listItemRegex.group(3).strip()
                ngramBackoff = float(listItemRegex.group(4) ) if listItemRegex.group(4) != None else None

                # TODO: check number of words
                ngramLogProbs[ngramOrder][words] = ngramLogProb
                ngramBackoffs[ngramOrder][words] = ngramBackoff
            elif line.strip() == '':
                continue
            elif line.strip() == '\\end\\':
                break
            else:
                raise Exception('Parsing Error at line {}: {}'.format(lineNumber, line))

    # TODO: CHeck if some data was read in.
    # TODO: Other validation?
    return {'ngramCounts': ngramCounts, 'ngramBackoffs': ngramBackoffs, 'ngramLogProbs': ngramLogProbs}

def calculateProp(ngram, arpaParse):
    ngramString = ' '.join(ngram)
    if ngramString in arpaParse['ngramLogProbs'][len(ngram)]:
        return arpaParse['ngramLogProbs'][len(ngram)][ngramString]
    elif len(ngram) == 1:
        return arpaParse['ngramLogProbs'][1]['<unk>']
    else:
        historyString = ' '.join(ngram[:-1])
        if historyString in arpaParse['ngramBackoffs'][len(ngram)-1]:
            return arpaParse['ngramBackoffs'][len(ngram)-1][historyString] + calculateProp(ngram[1:], arpaParse)
        else:
            return calculateProp(ngram[1:], arpaParse)

if __name__ == "__main__":
    main()