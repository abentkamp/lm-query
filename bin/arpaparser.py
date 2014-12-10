import re

class ArpaParser:
    def __init__(self, file):
        self.file = file
        self.__parse()
    
    def __parse(self):

        self.ngramCounts = {}
        self.ngramBackoffs = {}
        self.ngramLogProbs = {}
        beforeData = True
        lineNumber = 0

        self.file.seek(0)
        for line in self.file:
            lineNumber += 1

            if beforeData: 
                if line.strip() == '\\data\\':
                    beforeData = False
            else:
                ngramCountRegex = re.match('^ngram (\d+)=(\d+)$',line)
                listKeywordRegex = re.match('^\\\\(\d+)-grams:$',line)
                listItemRegex = re.match('^(-?\d+(\.\d+)?)(.+?)(-?\d+(\.\d+)?)?$',line)
                # TODO: Is more whitespace allowed?
                # TODO: What would be a reasonable way to tell apart a last word that is a float number and a backoff weight?

                if ngramCountRegex != None:
                    ngramOrder = int(ngramCountRegex.group(1))
                    ngramCount = int(ngramCountRegex.group(2))
                    self.ngramCounts[ngramOrder] = ngramCount
                elif listKeywordRegex != None:
                    ngramOrder = int(listKeywordRegex.group(1))
                    self.ngramLogProbs[ngramOrder] = {}
                    self.ngramBackoffs[ngramOrder] = {}
                elif listItemRegex != None:
                    ngramLogProb = float(listItemRegex.group(1))
                    words = listItemRegex.group(3).strip()
                    ngramBackoff = float(listItemRegex.group(4) ) if listItemRegex.group(4) != None else None

                    # TODO: check number of words
                    self.ngramLogProbs[ngramOrder][words] = ngramLogProb
                    self.ngramBackoffs[ngramOrder][words] = ngramBackoff
                elif line.strip() == '':
                    continue
                elif line.strip() == '\\end\\':
                    break
                else:
                    raise Exception('Parsing Error at line {}: {}'.format(lineNumber, line))
                    # TODO: raise a better Exception here

        # TODO: CHeck if some data was read in.
        # TODO: Other validation?





