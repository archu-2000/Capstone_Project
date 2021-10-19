#! /usr/bin/env python3


import json
import nltk
import re

from collections import defaultdict
from nltk.corpus import stopwords
from pattern.en import parse, Sentence, mood
from pattern.db import csv
from pattern.vector import Document, NB

def readText(fpath):

    with open(fpath, "r") as f:
        # text = f.read().decode('utf-8-sig')
        text = f.read()
    return text


def chunkSentences(text):
    sentences = nltk.sent_tokenize(text)
    tokenizedSentences = [nltk.word_tokenize(sentence)
                          for sentence in sentences]
    taggedSentences = [nltk.pos_tag(sentence)
                       for sentence in tokenizedSentences]
    if nltk.__version__[0:2] == "2.":
        chunkedSentences = nltk.batch_ne_chunk(taggedSentences, binary=True)
    else:
        chunkedSentences = nltk.ne_chunk_sents(taggedSentences, binary=True)
    return chunkedSentences


def extractEntityNames(tree, _entityNames=None):
    if _entityNames is None:
        _entityNames = []
    try:
        if nltk.__version__[0:2] == "2.":
            label = tree.node
        else:
            label = tree.label()
    except AttributeError:
        pass
    else:
        if label == 'NE':
            _entityNames.append(' '.join([child[0] for child in tree]))
        else:
            for child in tree:
                extractEntityNames(child, _entityNames=_entityNames)
    return _entityNames


def buildDict(chunkedSentences, _entityNames=None):

    if _entityNames is None:
        _entityNames = []

    for tree in chunkedSentences:
        extractEntityNames(tree, _entityNames=_entityNames)

    return _entityNames


def removeStopwords(entityNames, customStopWords=None):
    if customStopWords is None:
        with open("customStopWords.txt", "r") as f:
            customStopwords = f.read().split(', ')

    for name in entityNames:
        if name in stopwords.words('english') or name in customStopwords:
            entityNames.remove(name)


def getMajorCharacters(entityNames):
    return {name for name in entityNames if entityNames.count(name) > 10}


def splitIntoSentences(text):
    sentenceEnders = re.compile(r"""
    # Split sentences on whitespace between them.
    (?:               # Group for two positive lookbehinds.
      (?<=[.!?])      # Either an end of sentence punct,
    | (?<=[.!?]['"])  # or end of sentence punct and quote.
    )                 # End group of two positive lookbehinds.
    (?<!  Mr\.   )    # Don't end sentence on "Mr."
    (?<!  Mrs\.  )    # Don't end sentence on "Mrs."
    (?<!  Ms\.   )    # Don't end sentence on "Ms."
    (?<!  Jr\.   )    # Don't end sentence on "Jr."
    (?<!  Dr\.   )    # Don't end sentence on "Dr."
    (?<!  Prof\. )    # Don't end sentence on "Prof."
    (?<!  Sr\.   )    # Don't end sentence on "Sr."
    \s+               # Split on whitespace between sentences.
    """, re.IGNORECASE | re.VERBOSE)
    return sentenceEnders.split(text)


def compareLists(sentenceList, majorCharacters):
    characterSentences = defaultdict(list)
    for sentence in sentenceList:
        for name in majorCharacters:
            if re.search(r"\b(?=\w)%s\b(?!\w)" % re.escape(name),
                         sentence,
                         re.IGNORECASE):
                characterSentences[name].append(sentence)
    return characterSentences



def extractTones(characterSentences):

    nb = NB()
    characterTones = defaultdict(list)
    for review, rating in csv("dataset.csv"):
        nb.train(Document(review, type=int(rating), stopwords=True))
    for key, value in characterSentences.items():
        for x in value:
            characterTones[key].append(nb.classify(str(x)))
    return characterTones


def writeAnalysis(sentenceAnalysis):
    with open("sentenceAnalysis.txt", "w") as f:
        for item in sentenceAnalysis.items():
            f.write("%s:%s\n" % item)
            
def writeToJSON(sentenceAnalysis, loc):
	with open(loc+"/sentenceAnalysis.json", "w") as f:
		entities = sentenceAnalysis.keys()
		json.dump(sentenceAnalysis, f)
'''
if __name__ == "__main__":
    text = readText()

    chunkedSentences = chunkSentences(text)
    # print(list(chunkedSentences))
    entityNames = buildDict(chunkedSentences)
    # print(list(entityNames))
    removeStopwords(entityNames)
    majorCharacters = getMajorCharacters(entityNames)
    # print(list(majorCharacters))
    
    sentenceList = splitIntoSentences(text)
    characterSentences = compareLists(sentenceList, majorCharacters)
    # print(list(characterSentences))
  
    characterTones = extractTones(characterSentences)

    sentenceAnalysis = defaultdict(list,[(k, [characterSentences[k], characterTones[k]]) for k in characterSentences])
    print(sentenceAnalysis)
    # writeAnalysis(sentenceAnalysis)
 '''
