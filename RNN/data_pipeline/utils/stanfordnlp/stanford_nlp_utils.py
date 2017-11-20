#!/usr/bin/python2
from pycorenlp import StanfordCoreNLP
import re
# nlp = StanfordCoreNLP('http://13.67.115.74:9000')
# nlp = StanfordCoreNLP('http://119.63.99.173:9000')

# nlp = StanfordCoreNLP('http://13.67.115.74:9000')
# nlp = StanfordCoreNLP('http://13.67.115.74:9000')

# nlp = StanfordCoreNLP('http://localhost:9000')
nlp = StanfordCoreNLP('http://192.168.0.100:9000')


def stanford_tree(line, annotators='parse lemma'):
    output = nlp.annotate(line, properties={
        'annotators': annotators,
        'outputFormat': 'json'
    })
    try:
        return output
    except IndexError:
        pass


def generate_clean_stanford_tree(msg):
    """
    input a sentence, return a parsed stanford tree
    node with a punctuation label will be deleted. e.g.:(, ,)
    node with -LRB-, -RRB- label will be deleted. e.g.:(-LRB- -LRB-), (-RRB- -RRB-))

    :param msg: sentence
    :return: lisp style stanford tree
    """
    # for python 2
    try:
        raw_result = stanford_tree(str(msg))
    except UnicodeEncodeError:
        lisp_tree = 'BADTREE'
        return lisp_tree

    # for python 3
    #raw_result = stanford_tree(msg)
    try:
        lisp_tree = raw_result['sentences'][0]['parse']
        # print lisp_tree
        # remove endlines in original parsed tree
        lisp_tree = re.sub(r"(\s\s)+", '', lisp_tree, flags=re.IGNORECASE)
        # print lisp_tree
        # remove punc after getting the parsed tree
        lisp_tree = re.sub(r' \([^\(\w\s]+ [^\w\s\)]+\)', '', lisp_tree, flags=re.IGNORECASE)
        lisp_tree = re.sub(r'\([^\(\w\s]+ [^\w\s\)]+\) ', '', lisp_tree, flags=re.IGNORECASE)
        # print lisp_tree
        # remove brackets
        lisp_tree = lisp_tree.replace(' (-LRB- -LRB-)', '')
        lisp_tree = lisp_tree.replace(' (-RRB- -RRB-)', '')
        lisp_tree = lisp_tree.replace('(-LRB- -LRB-) ', '')
        lisp_tree = lisp_tree.replace('(-RRB- -RRB-) ', '')
        if re.findall('(\(-LRB-)|(\(-RRB-)|(\(-RSB-)|(\(-LSB-)', lisp_tree):
            print lisp_tree
            return 'BADTREE'
        # print lisp_tree
    except RuntimeError:
        lisp_tree = 'BADTREE'
    return lisp_tree


def replace_tree_label(str_tree):
    """
    replace the POS tag with number
    :param str_tree: flat lisp style tree
    :return: str_tree after replace POS tag with number
    """
    dic_tag = {'ROOT': 0, 'S': 1, 'SBAR': 2, 'SBARQ': 3, 'SINV': 4, 'SQ': 5, 'NP-TMP': 6, 'ADJP': 7, 'ADVP': 8,
               'CONJP': 9,
               'FRAG': 10, 'INTJ': 11, 'LST': 12, 'NAC': 13, 'NP': 14, 'NX': 15, 'PP': 16, 'PRN': 17,
               'PRT': 18,
               "QP": 19, "RRC": 20, "UCP": 21, "VP": 22, "WHADJP": 23, "WHADVP": 24, "WHNP": 25, "WHPP": 26,
               "X": 27, 'CC': 28, 'CD': 29, 'DT': 30, 'EX': 31, 'FW': 32, 'IN': 33, 'JJ': 34, 'JJR': 35,
               'JJS': 36,
               'LS': 37, 'MD': 38, 'NN': 39, 'NNS': 40, 'NNP': 41, 'NNPS': 42, 'PDT': 43, 'POS': 44,
               'PRP$': 46, 'RB': 47, 'RBR': 48, 'RBS': 49, 'RP': 50, 'SYM': 51, 'TO': 52, 'UH': 53, 'VB': 54,
               'VBD': 55, 'VBG': 56, 'VBN': 57, 'VBP': 58, 'VBZ': 59, 'WDT': 60, 'WP': 61, 'WP$': 62,
               'WRB': 63,
               'ADV': 64, 'NOM': 65, 'DTV': 66, 'LGS': 67, 'PRD': 68, 'PUT': 69, 'SBJ': 70, 'TPC': 71,
               'VOC': 72,
               'BNF': 73, 'DIR': 74, 'EXT': 75, 'LOC': 76, 'MNR': 77, 'PRP': 78, 'TMP': 79, 'CLR': 80}

    label_pattern = '\([A-Z]+'
    ls_str_tree = str_tree.split(' ')
    for i in range(0, len(ls_str_tree)):
        token = ls_str_tree[i]
        if re.findall(label_pattern, token, flags=re.IGNORECASE):
            # print(token)
            key = token[1:]
            if key in dic_tag.keys():
                ls_str_tree[i] = '(' + str(dic_tag[token[1:]])
            else:
                print('POS tag not found in dic:', key, 'is missing')
                return 'BADTREE'

    new_str_tree = ' '.join(ls_str_tree)  # Forming string
    print new_str_tree
    return new_str_tree
