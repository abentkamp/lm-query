lm-query
========

**lm-query** queries a language model specified in an [ARPA file](http://www.speech.sri.com/projects/srilm/manpages/ngram-format.5.html).

Given an ARPA file and some test data, it will output the following:

* For each word it outputs a line of the format     
  `[word]=[known word?] [n-gram length] [log10 probability]`
  * `[word]` is the current word.
  * `[known word?]` is 0 for unseen words (OOVs) and 1 if the word was in the training set.
  * `[n-gram length]` is the length of the n-gram that was found for this word. That is how many words of the history (including the word itself) could be used to determine the probability.
  * `[log10 probability]` is the log 10 probability that was assigned for this word to appear in this context by the language model.
* At the end of each sentence the total log 10 probability of the sentence is given, as well as the number of OOV words.
* At the end of the querying process, the program will output the following to stderr:
  * Perplexity, inlcluding and excluding OOVs. Excluding OOVs means that unknown words are simply ignored.
  * Number of OOVs in the test data.
  * Number of tokens (words) in the test data.
  * The execution time for querying the language model.

Requirements
------------
* Python 3.x

Installation
-------------
**For Windows**: You can download the zip folder from github and unzip the file. Alternatively, you can download the program via GitHub Windows.

**For Linux**: In the terminal run `git clone https://github.com/benti/lm-query.git`. Alternatively you can download the zip folder from github and unzip the file.

How to use it
-------------

Make sure the test data file seperates words by spaces and sentences by line breaks.

**For Windows**: open the command prompt, go to lm-query folder, 
run 

`python bin\lm-query.py [arpa file] < [test data file] > [probability output file] 2> [perplexity output file]`


**For Linux**: In the terminal run 

`lm-query/bin/lm-query.py [arpa file] < [test data file] > [probability output file] 2> [perplexity output file]`


Licence
-------
[The MIT License (MIT)](https://github.com/benti/lm-query/blob/master/LICENSE)
