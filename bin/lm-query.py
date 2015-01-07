#!/usr/bin/env python2.7
import argparse
import sys
import math
import re

def main():

    args = parseArguments()

    arpaParse = parseArpa(args.arpa_file)

    # log probability for the whole test set
    totalLogProb = 0

    # log prob of the whole test set, ignoring the oovs
    totalLogProbExclOov = 0

    # Total number of words in the test set
    wordCount = 0

    # counts the unknown words
    oovCount = 0

    # iterate over the sentences in the test data
    for sentence in args.test_data:
        sentence = sentence.strip()

        # list of previous words in the sentence
        history = ['<s>']

        # list of all the words in the sentence
        wordList = sentence.split(' ');
        wordList.append('</s>')

        # log prob of the whole sentence
        sentenceTotalLogProb = 0

        # number of oovs in the sentence
        sentenceOovCount = 0

        # iterate over the words in the sentence
        for word in wordList:
            history.append(word)
            # remove words in the history that are too long ago
            if len(history) not in arpaParse['ngramLogProbs']:
                history.pop(0)

            # Calculate proabability for the word given the history
            wordId, length, wordLogProb = calculateProp(history, arpaParse)

            sentenceTotalLogProb += wordLogProb
            totalLogProb += wordLogProb
            wordCount += 1

            if wordId == 0: # unknown word
                oovCount += 1
                sentenceOovCount += 1
            else:
                totalLogProbExclOov += wordLogProb

            print ('{}={} {} {}'.format(word, wordId, length, wordLogProb))

        
        print ('Total: {} OOV: {}'.format(sentenceTotalLogProb, sentenceOovCount))

    perplexity = math.pow(10, -totalLogProb/wordCount)
    perplexityExclOov = math.pow(10, -totalLogProbExclOov/(wordCount-oovCount))
    
    print ('Perplexity including OOVs: {}'.format(perplexity), file=sys.stderr)
    print ('Perplexity excluding OOVs: {}'.format(perplexityExclOov), file=sys.stderr)
    print ('OOVs: {}'.format(oovCount), file=sys.stderr)
    print ('Tokens: {}'.format(wordCount), file=sys.stderr)

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
            # Only start parsing when the '\data\' keyword occurs
            if line.strip() == '\\data\\':
                beforeData = False
        else:
            ngramCountRegex = re.match('^ngram (\d+)=(\d+)$',line)
            listKeywordRegex = re.match('^\\\\(\d+)-grams:$',line)

            # A line like 'ngram 2=27866'
            if ngramCountRegex != None:
                ngramOrder = int(ngramCountRegex.group(1))
                ngramCount = int(ngramCountRegex.group(2))
                ngramCounts[ngramOrder] = ngramCount

            # A line like '\2-grams:'
            elif listKeywordRegex != None:
                ngramOrder = int(listKeywordRegex.group(1))
                ngramLogProbs[ngramOrder] = {}
                ngramBackoffs[ngramOrder] = {}

            # An empty line
            elif line.strip() == '':
                continue

            # A line like '\end\'
            elif line.strip() == '\\end\\':
                break

            # A line like '-1.9320396   the universe works  -0.031235874'      
            elif ngramOrder != None:
                # seperate the line with white space as delimter
                splitLine = line.split()      

                # the second to the n+1 th parts are the words of the ngram
                words = ' '.join(splitLine[1:1+ngramOrder]) 

                # The first part is the log prbability of the ngram
                ngramLogProbs[ngramOrder][words] = float(splitLine[0])

                # if there is one more part, it's the backoff
                if(len(splitLine) > ngramOrder + 1):
                    ngramBackoffs[ngramOrder][words] = float(splitLine[-1])

            # Anything else
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
