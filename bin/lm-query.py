#!/usr/bin/env python2.7
import argparse
import sys
import math
import re

def main():

    args = parseArguments()

    arpaParse = parseArpa(args.arpa_file)

    # TODO: support UTF8 encoding
    totalLogProb = 0
    totalLogProbExclOov = 0
    wordCount = 0
    oovCount = 0
    for sentence in args.test_data:
        sentence = sentence.strip()
        history = ['<s>']
        wordList = sentence.split(' ');
        wordList.append('</s>')
        sentenceTotalLogProb = 0
        sentenceOovCount = 0
        for word in wordList:
            history.append(word)
            if len(history) not in arpaParse['ngramLogProbs']:
                history.pop(0)

            wordId, length, wordLogProb = calculateProp(history, arpaParse)

            sentenceTotalLogProb += wordLogProb
            totalLogProb += wordLogProb
            wordCount += 1

            if wordId == 0: # unknown word
                oovCount += 1
                sentenceOovCount += 1
            else:
                totalLogProbExclOov += wordLogProb

            print '{}={} {} {}'.format(word, wordId, length, wordLogProb)

        
        print 'Total: {} OOV: {}'.format(sentenceTotalLogProb, sentenceOovCount)

    perplexity = math.pow(10, -totalLogProb/wordCount)
    perplexityExclOov = math.pow(10, -totalLogProbExclOov/(wordCount-oovCount))

    print >> sys.stderr, 'Perplexity including OOVs: {}'.format(perplexity)
    print >> sys.stderr, 'Perplexity excluding OOVs: {}'.format(perplexityExclOov)
    print >> sys.stderr, 'OOVs: {}'.format(oovCount)
    print >> sys.stderr, 'Tokens: {}'.format(wordCount)

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

# This function returns three values:
# - A fake word id, which is 0 if the word is unknown or 1 if the word is known from training
# - The length of the ngram used to determine the probability
# - The log probability of the word
def calculateProp(ngram, arpaParse):
    # The ngramString is the words seperated by spaces
    ngramString = ' '.join(ngram)

    # if the ngram is in the training data, return the probability.
    if ngramString in arpaParse['ngramLogProbs'][len(ngram)]:
        return 1, len(ngram), arpaParse['ngramLogProbs'][len(ngram)][ngramString]

    # if the ngram is a unknown unigram, return the <unk> probability.
    elif len(ngram) == 1:
        return 0, 1, arpaParse['ngramLogProbs'][1]['<unk>']

    # if the ngram is unknown and not a unigram, shorten the history.
    else:
        historyString = ' '.join(ngram[:-1])
        if historyString in arpaParse['ngramBackoffs'][len(ngram)-1]:
            id, length, prob = calculateProp(ngram[1:], arpaParse)
            return id, length, arpaParse['ngramBackoffs'][len(ngram)-1][historyString] + prob
        else:
            return calculateProp(ngram[1:], arpaParse)

if __name__ == "__main__":
    main()