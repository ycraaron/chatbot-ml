from data_pipeline.binary_tree.lexica_binary_tree import LexicaBinaryTree
from data_pipeline.utils.stanfordnlp.stanford_nlp_utils import generate_clean_stanford_tree, replace_tree_label


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
            self.label = None
            self.msg1 = ''
            self.msg2 = ''
            self.str_tree1 = ''
            self.str_tree2 = ''
        else:
            print('You are running in debug mode to test with single sentence.')
            print('Call LexicaParaphrasedData.debug_function() as needed.')
        # self.btree = BinaryTree()

    def process_sentence_pairs(self):
        """
        process the input paraphrased data
        write to output folder about the binary tree
        """
        for record in self.ls_records:
            ls_split_record = self.split_record(record)
            if self.data_source == 'microsoft':
                if len(ls_split_record) != 5:
                    continue
                self.label = ls_split_record[0]
                self.msg1 = self.clean_msg(ls_split_record[3])
                self.msg2 = self.clean_msg(ls_split_record[4])
            elif self.data_source == 'quora':
                if len(ls_split_record) != 6:
                    continue
                self.label = ls_split_record[5].strip('\n')
                self.msg1 = self.clean_msg(ls_split_record[3])
                self.msg2 = self.clean_msg(ls_split_record[4])
            self.parse_msg_pair_to_tree()

            self.binary_tree_pair_transform()

            if self.str_tree1 != 'BADTREE' and self.str_tree2 != 'BADTREE':
                dic = {'label': self.label, 'tree1': self.str_tree1, 'tree2': self.str_tree2}
                self.output_record(dic)
            else:
                if self.str_tree1 == 'BADTREE':
                    print('tree 1 false', self.msg1)
                else:
                    print('tree 1 OK:', self.str_tree1)
                if self.str_tree2 == 'BADTREE':
                    print('tree 2 false', self.msg2)
                else:
                    print('tree 2 OK :', self.str_tree2)

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

    def binary_tree_pair_transform(self):
        """
        transform classmember str_tree1 and str_tree2 to binary flat tree
        :return: False or a flat binary lisp style tree
        """
        if self.str_tree1 == 'BADTREE':
            pass
        else:
            self.str_tree1 = LexicaBinaryTree(self.str_tree1).get_str_flat_binary_tree()

        if self.str_tree2 == 'BADTREE':
            pass
        else:
            self.str_tree2 = LexicaBinaryTree(self.str_tree2).get_str_flat_binary_tree()

    def parse_msg_pair_to_tree(self):
        """
        remove the noise in the msg and replace the POS tag with number
        :param msg: input microsoft data sentence
        :return: tree with replaced label
        """
        flat_str_tree1 = generate_clean_stanford_tree(self.msg1.replace('\n', ''))
        flat_str_tree2 = generate_clean_stanford_tree(self.msg2.replace('\n', ''))
        # print(falt_str_tree)
        self.str_tree1 = replace_tree_label(flat_str_tree1)
        self.str_tree2 = replace_tree_label(flat_str_tree2)
        # print(str_tree)

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
