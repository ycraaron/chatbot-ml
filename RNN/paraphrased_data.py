import re

from data_pipeline.binary_tree.lexica_binary_tree import LexicaBinaryTree

from data_pipeline.utils.stanfordnlp.stanford_connector import stanford_tree


class LexicaParaphrasedData(object):
    def __init__(self, file_input='', file_output='', splitter='', datasource='', debug=False):
        """
        :param file_input: input data file
        :param file_output: path to ouput file
        :param splitter: the splitter between label@splitter@sentence1@splitter@sentence2
        :param data_source = microsoft/quora for now
        """
        if not debug:
            self.data_source = datasource
            self.splitter = splitter
            self.fid_input = open(file_input, 'rb')
            self.fid_output = open(file_output, 'wb')
            self.ls_records = [line.decode('utf-8') for line in self.fid_input.readlines()]
            self.replaced_label = {}
            self.dic_tag = {'ROOT': 0, 'S': 1, 'SBAR': 2, 'SBARQ': 3, 'SINV': 4, 'SQ': 5, 'ADJP': 7, 'ADVP': 8, 'CONJP': 9,
                        'FRAG': 10, 'INTJ': 11, 'LST': 12, 'NAC': 13, 'NP': 14, 'NX': 15, 'PP': 16, 'PRN': 17, 'PRT': 18,
                        "QP": 19, "RRC": 20, "UCP": 21, "VP": 22, "WHADJP": 23, "WHADVP": 24, "WHNP": 25, "WHPP": 26,
                        "X": 27, 'CC': 28, 'CD': 29, 'DT': 30, 'EX': 31, 'FW': 32, 'IN': 33, 'JJ': 34, 'JJR': 35, 'JJS': 36,
                        'LS': 37, 'MD': 38, 'NN': 39, 'NNS': 40, 'NNP': 41, 'NNPS': 42, 'PDT': 43, 'POS': 44,
                        'PRP$': 46, 'RB': 47, 'RBR': 48, 'RBS': 49, 'RP': 50, 'SYM': 51, 'TO': 52, 'UH': 53, 'VB': 54,
                        'VBD': 55, 'VBG': 56, 'VBN': 57, 'VBP': 58, 'VBZ': 59, 'WDT': 60, 'WP': 61, 'WP$': 62, 'WRB': 63,
                        'ADV': 64, 'NOM': 65, 'DTV': 66, 'LGS': 67, 'PRD': 68, 'PUT': 69, 'SBJ': 70, 'TPC': 71, 'VOC': 72,
                        'BNF': 73, 'DIR': 74, 'EXT': 75, 'LOC': 76, 'MNR': 77, 'PRP': 78, 'TMP': 79, 'CLR': 80}
        else:
            print('You are running in debug mode to test with single sentence.')
            print('Call LexicaParaphrasedData.debug_function() as needed.')
        # self.btree = BinaryTree()

    def process_data(self):
        """
        process the input paraphrased data

        write to output folder about the binary tree
        """
        for record in self.ls_records:
            ls_split_record = self.split_record(record)

            if self.data_source == 'microsoft':
                if len(ls_split_record) != 5:
                    continue
                label = ls_split_record[0]
                msg1 = self.clean_msg(ls_split_record[3])
                msg2 = self.clean_msg(ls_split_record[4])
            elif self.data_source == 'quora':
                if len(ls_split_record) != 6:
                    continue
                label = ls_split_record[5].strip('\n')
                msg1 = self.clean_msg(ls_split_record[3])
                msg2 = self.clean_msg(ls_split_record[4])

            str_tree1 = self.parse_msg(msg1)
            str_tree2 = self.parse_msg(msg2)

            str_tree1 = self.binary_tree_transform(str_tree1)
            str_tree2 = self.binary_tree_transform(str_tree2)
            if str_tree1 is not False and str_tree2 is not False:
                dic = {'label': label, 'tree1': str_tree1, 'tree2': str_tree2}
                self.output_record(dic)
            else:
                if str_tree1 is False:
                    print('tree 1 false', msg1)
                else:
                    print('tree 1 OK:', str_tree1)
                if str_tree2 is False:
                    print('tree 2 false', msg2)
                else:
                    print('tree 2 OK :', str_tree2)

    def output_record(self, dic):
        """
        save the label@@@@tree1@@@@tree2
        :param dic: dictionary store {label, tree1, tree2}
        """
        label = dic['label']
        tree1 = dic['tree1']
        tree2 = dic['tree2']
        str_output = label + '@@@@' + tree1 + '@@@@' + tree2
        # print(str_output)
        self.fid_output.write(str_output.encode('utf-8'))
        self.fid_output.write('\n'.encode('utf-8'))

    @staticmethod
    def binary_tree_transform(str_tree):
        """
        :param str_tree: lisp style tree string
        :return: False or a flat binary lisp style tree
        """
        if str_tree == 'BADTREE':
            return False

        result = LexicaBinaryTree(str_tree).generate_flat_binary_tree()
        if result == 'BADTREE':
            return False
        else:
            return result

    def parse_msg(self, msg):
        """
        remove the noise in the msg and replace the POS tag with number
        :param msg: input microsoft data sentence
        :return: tree with replaced label
        """
        flat_str_tree = self.generate_stanford_tree(msg).replace('\n', '')
        # print(falt_str_tree)
        str_tree = self.replace_tree_label(flat_str_tree)
        # print(str_tree)
        return str_tree

    def replace_tree_label(self, str_tree):
        """
        replace the POS tag with number
        :param str_tree: flat lisp style tree
        :return: str_tree after replace POS tag with number
        """
        # tokens = word_tokenize(str_tree)
        label_pattern = '\([A-Z]+'
        ls_str_tree = str_tree.split(' ')
        for i in range(0, len(ls_str_tree)):
            token = ls_str_tree[i]
            if re.findall(label_pattern, token, flags=re.IGNORECASE):
                # print(token)
                key = token[1:]
                if key in self.dic_tag.keys():
                    ls_str_tree[i] = '(' + str(self.dic_tag[token[1:]])
                else:
                    print('POS tag not found in dic:', key, 'is missing')
                    return 'BADTREE'

        # for t, i in enumerate(tokens):
        #     if i in self.dic_tag.keys():
        #         tokens[t] = str(self.dic_tag[i])  # Encode tags to dictionary index
        new_str_tree = ' '.join(ls_str_tree)  # Forming string
        # print(new_str_tree)
        # print(str_tree)
        # str_tree = re.sub(r"\(\s(.|,)\s(.|,)\s\)", "", str_tree)  # Remove punctuation parse glitch
        return new_str_tree

    @staticmethod
    def generate_stanford_tree(msg):
        """
        input a sentence, return a parsed stanford tree
        :param msg: sentence
        :return: lisp style stanford tree
        """
        """
        :param msg: string msg
        :return: lisp style tree generated by stanfordNLP parser
        """
        raw_result = stanford_tree(msg)
        # print(raw_result)
        # tokens = raw_result['sentences'][0]['tokens']
        # lisp_tree = raw_result['sentences'][0]['parse']
        # lisp_tree = re.sub(r"(\s\s)+", ' ', lisp_tree)
        # draw_trees(ParentedTree.fromstring(lisp_tree))
        # # remove punc afterwards
        # lisp_tree = re.sub(r'\([^\w\s] .\)', '', lisp_tree)
        # draw_trees(ParentedTree.fromstring(lisp_tree))
        # print(lisp_tree)
        # nltk_tree = ParentedTree.fromstring(lisp_tree)
        # sub_trees = nltk_tree.subtrees()
        # leaves = nltk_tree.leaves()
        # # print('new leaves', leaves)
        #
        # for leaf in leaves:
        #     if re.findall(r'\([^\w\s] .\)', label):
        #         leaf_index = leaves.index(leaf)
        #         tree_position = self.nltk_tree.leaf_treeposition(leaf_index)
        #         parent = tree_position[:-1]
        #         del self.nltk_tree[parent]  # delete the merged subtrees
        # for sub_tree in sub_trees:
        #     label = sub_tree.label()
        #     if re.findall(r'[A-Z]+', label):
        #         continue
        #     else:
        #         del sub_tree
        #         print(sub_tree)
        #         print(label)
        # print(tokens)
        # quit()
        try:
            lisp_tree = raw_result['sentences'][0]['parse']
            lisp_tree = re.sub(r"(\s\s)+", ' ', lisp_tree)
            # draw_trees(ParentedTree.fromstring(lisp_tree))
            # remove punc afterwards
            lisp_tree = re.sub(r'\([^\(\w\s]+ [^\w\s\)]+\)', '', lisp_tree)
            # draw_trees(ParentedTree.fromstring(lisp_tree))

        except TypeError:
            return 'BADTREE'
        return lisp_tree

    def split_record(self, record):
        """
        :param record: the line in paraphrased data file
        :return: a list for record splitted by the splitter
        """
        return record.split(self.splitter)

    def debug_get_binary_tree_obj(self, sentence):
        lisp_tree_str = self.generate_stanford_tree(sentence)
        self.binary_tree_transform(lisp_tree_str)



    @staticmethod
    def clean_msg(msg):
        msg = msg.strip()
        return msg
