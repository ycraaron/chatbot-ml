#!/usr/bin/python3
from pycorenlp import StanfordCoreNLP
import os

# nlp = StanfordCoreNLP('http://13.67.115.74:9000')
# nlp = StanfordCoreNLP('http://119.63.99.173:9000')

if os.environ.get('LEXICA') == True or os.environ.get('LEXICA') == "true":
    # nlp = StanfordCoreNLP('http://192.168.0.100:9000')
    nlp = StanfordCoreNLP('http://localhost:9000')
else:
    nlp = StanfordCoreNLP('http://13.67.115.74:9000')

# nlp = StanfordCoreNLP('http://13.67.115.74:9000')

# nlp = StanfordCoreNLP('http://localhost:9000')
nlp = StanfordCoreNLP('http://192.168.0.100:9000')


def stanford_tree(line, annotators='parse'):
    output = nlp.annotate(line, properties={
        'annotators': annotators,
        'outputFormat': 'json'
    })
    try:
        return output
    except IndexError:
        pass
