import re

from multiprocessing import Queue

# disable draw tree on server
from nltk.draw.tree import draw_trees

from nltk.tree import ParentedTree
from data_pipeline.binary_tree.tree import Tree
from data_pipeline.utils.stanfordnlp.stanford_nlp_utils import generate_clean_stanford_tree, replace_tree_label


class LexicaBinaryTree(object):
    """
    take a parsed tree with labels replaced as input
    call get_str_flat_binary_tree() to get the flat binary tree

    debug mode:
        call debug_get_tree_obj_from_sentence(sentence) to get a binary Tree object
    """
    def __init__(self, str_tree='', is_binary_tree_input=False, debug=False):
        if not debug:
            if is_binary_tree_input:
                self.str_flat_binary_tree = str_tree
            else:
                self.str_tree = str_tree
                self.str_flat_binary_tree = ''
                self.nltk_tree = None
                self.bad_tree = False
                self.build_nltk_tree()
        else:
            print('You are running in debug mode to test with single sentence.')
            print('Call function with DEBUG prefix as needed.')
            self.debug = True
            self.str_tree = ''
            self.str_flat_binary_tree = ''
            self.bad_tree = False
            self.nltk_tree = None

    # deprecated since there were some misunderstandings at the beginning
    # use it only when you want to add a null leaf to every leaf parent to make them binary.
    def debug_get_tree_obj_from_sentence(self, sentence):
        self.str_tree = generate_clean_stanford_tree(sentence)
        print self.str_tree
        self.str_tree = '(ROOT (SBARQ (WHNP) (SQ (VP (NP (SBAR (WHADVP (WRB How)) (S (VP (TO to) (VP (VB move) (NP (NP (JJ pre)) (FRAG (S (VP (VBN installed) (NP (NNS apps)) (PP (TO to) (NP (NN SD) (NN card))))))))))))))))'
        if self.str_tree != 'BADTREE':
            self.str_tree = replace_tree_label(self.str_tree)
        if self.str_tree == 'BADTREE':
            self.bad_tree = True
            self.str_flat_binary_tree = 'BADTREE'
            return 'BADTREE'
        self.str_flat_binary_tree = ''
        self.nltk_tree = None
        self.build_nltk_tree()
        return Tree(self.str_flat_binary_tree)

    def bfs(self):
        """
        print the bfs result of the tree
        Returns: None
        """
        # print('BFSing the tree to check NONE type')
        tree_obj = Tree(self.str_flat_binary_tree)
        if tree_obj.root is None:
            return False
        queue = Queue()
        ls_queue = []
        # queue.put_nowait(tree_obj.root)
        ls_queue.append(tree_obj.root)
        # sleep(0.01)
        # print(tree_obj.root)
        while not len(ls_queue) == 0:
            # node = queue.get()
            node = ls_queue[0]
            del ls_queue[0]
            # print(node.label, '->', node.word)
            if node.left is not None:
                ls_queue.append(node.left)
                # queue.put_nowait(node.left)
                # sleep(0.01)
            else:
                if node.word is not None:
                    pass
                    # print('leaf detected')
                else:
                    print 'None type node finded, BADTREE', self.str_flat_binary_tree
                    self.str_flat_binary_tree = 'BADTREE'
                    self.bad_tree = True
                    return False
            if node.right is not None:
                ls_queue.append(node.right)
                # queue.put_nowait(node.right)
                # sleep(0.01)
            else:
                if node.word is not None:
                    pass
                    # print('leaf detected')
                else:
                    print 'None type node finded, BADTREE', self.str_flat_binary_tree
                    self.str_flat_binary_tree = 'BADTREE'
                    self.bad_tree = True
                    return False
        return True

    def add_leaves(self):
        ls_leaves = self.nltk_tree.leaves()
        ls_leaf_indices = [ls_leaves.index(leaf) for leaf in ls_leaves]
        for i in range(0, len(ls_leaf_indices)):
            leaf_tree_location = self.nltk_tree.leaf_treeposition(ls_leaf_indices[i])
            parent_position = leaf_tree_location[:-1]
            self.nltk_tree[parent_position].append('@@')
            for j in range(i, len(ls_leaf_indices)):
                ls_leaf_indices[j] += 1

    # get all the leaves
    def get_leaf_position(self):
        """
        :return: a list of leaf position of the tree
        """
        ls_leaves = self.nltk_tree.leaves()
        # print(ls_leaves)
        # ls_leaf_indices = [ls_leaves.index(leaf) for leaf in ls_leaves]
        ls_leaf_indices = []
        for leaf in ls_leaves:
            index = ls_leaves.index(leaf)
            if index in ls_leaf_indices:
                for i in range(index, len(ls_leaves)):
                    if ls_leaves[i] == leaf and (i not in ls_leaf_indices):
                        ls_leaf_indices.append(i)
                        break
            else:
                ls_leaf_indices.append(index)
        # print(ls_leaf_indices)
        ls_leaf_position = []
        for leaf in ls_leaf_indices:
            leaf_tree_location = self.nltk_tree.leaf_treeposition(leaf)
            ls_leaf_position.append(leaf_tree_location)
        return ls_leaf_position

    @staticmethod
    def load_trees(tree_file='data_files/trees/wiki_09_tree_out.txt'):
        file = tree_file
        ls_trees = []
        with open(file, 'rb') as fid_tree:
            content = fid_tree.readlines()
            for tree in content:
                tree_str = tree.decode('utf-8')
                if re.findall(r'[1-9]+ \'', tree_str):
                    continue
                else:
                    ls_trees.append(tree_str)
        return ls_trees

    def build_nltk_tree(self):
        self.nltk_tree = ParentedTree.fromstring(self.str_tree).pop() # pop the root node generated by stanfordCoreNLP
        self.generate_flat_binary_tree()
        if not self.bad_tree:
            self.bfs()

    def find_max_children(self):
        """
        check whether a tree have more than 5 children
        :return: True if the tree have more than 5 children.
        """
        tree_positions = self.nltk_tree.treepositions()
        for position in tree_positions:
            for index in position:
                if index > 4:
                    return True
        return False

    # generate the layer information of a tree
    # prune all the leaves
    def generate_layer_dic(self, leaves):
        """
        generate a dictionary stores every layer of a tree
        :param leaves: all leaves positions in the nltk_tree
        :return: return a dictionary which stores every layer of the tree
        """
        ls_tree_position = self.nltk_tree.treepositions()
        height = self.nltk_tree.height()
        dic_tree = {}
        for i in range(0, height):
            dic_tree[i] = []
        for position in ls_tree_position:
            if position not in leaves:
                dic_tree[len(position)].append(position)
        return dic_tree

    @staticmethod
    def find_layer_parent(layer, ls_layer):
        """
        find the parents node of current layer, and find the target parent node(non binary tree : only have 1 child or more than 2 children)
        :param layer: current layer number we are dealing with
        :param ls_layer: node positions in this layer
        :return: parents stored in dictionary {'parent': (position), 'max': num_of_children } for the nodes in this layer:
                 ls_layer_parent:           store all the parents.
                 ls_layer_parent_multiple:  store the parents with more than 2 children.
                 ls_layer_parent_single:    store the parents with only 1 child.
        """

        # 0 represents the top layer
        if ls_layer and layer > 0:
            # print(ls_layer)
            ls_layer_parent = []
            ls_layer_parent_multiple = []   # store the parent with more than two children
            ls_layer_parent_single = []     # store the parent with single child
            for child_node_position in ls_layer:
                # the position among all children [0-n] (n > 0)
                parent = child_node_position[:-1]
                if parent not in ls_layer_parent:
                    ls_layer_parent.append(parent)

            # loop through the layer again, to find max child num for each parent
            for parent in ls_layer_parent:
                max_child_num = 0
                for child_node_position in ls_layer:
                    child_parent = child_node_position[:-1]
                    if parent == child_parent:
                        # last element in tuple represents the num of children
                        # e.g: the parent of node (0, 2, 1, 3, 3) has at least 4 children
                        cnt_child = child_node_position[len(child_node_position) - 1]
                        if cnt_child > max_child_num:
                            max_child_num = cnt_child
                if max_child_num == 0:
                    ls_layer_parent_single.append(parent)
                if max_child_num > 1:
                    ls_layer_parent_multiple.append({'parent': parent, 'max': max_child_num})

            return ls_layer_parent, ls_layer_parent_multiple, ls_layer_parent_single
        else:
            # print('empty layer:', layer)
            return [], [], []

    def tree_transformation(self, parent, ls_pos_children=[], type=''):
        """
        transform a non binary tree to binary tree.
        :param parent: parent position of nltk_tree
        :param ls_pos_children: for multiple situation, the positions of the potential children of the parent
        :param type: single, tree with on child. multiple, tree with more than 2 children
        :return: return a binary nltk.ParentTree object
        """
        if type == 'single':
            # print('single tree component')
            self.nltk_tree[parent].append(ParentedTree(self.nltk_tree[parent].label(), ['@@']))
            return True
        elif type == 'multiple':
            # print('multiple tree component')
            tup_position_parent = parent['parent']
            tree_parent = self.nltk_tree[tup_position_parent]
            cnt_children = parent['max']
            cnt_sub_tree_pair = int((cnt_children + 1) / 2)     # calculate the number of children pairs
            remainder = (cnt_children + 1) % 2                  # 0 -> even, 1 -> odd
            for i in range(0, cnt_sub_tree_pair):
                pos_tree1 = ls_pos_children[2 * i]              # pick out
                pos_tree2 = ls_pos_children[2 * i + 1]          # subtree pair
                tree1 = self.nltk_tree[pos_tree1]
                tree2 = self.nltk_tree[pos_tree2]
                label_parent = tree_parent.label()              # get parent label
                str_tree1 = str(tree1)
                str_tree2 = str(tree2)                          # build a new subtree with these two chindren
                tree_parent.append(ParentedTree(label_parent, [ParentedTree.fromstring(str_tree1),
                                                               ParentedTree.fromstring(str_tree2)])) # append the new subtree to the end of the parent
            if remainder != 0:
                pos_remaining_child = ls_pos_children[len(ls_pos_children) - 1]
                tree_remaining = self.nltk_tree[pos_remaining_child]
                # print('remaining tree', tree_remaining)
                tree_parent.append(tree_remaining.copy(deep=True))

            for child in ls_pos_children:
                # print(nltk_tree[child], 'will be replaced')
                self.nltk_tree[child] = ParentedTree('LEXICA_REPLACED', ['lexica_replaced_leaf']) # replace the merged subtree with specific symbol in order to delete them

            # draw_trees(nltk_tree)
            # remove the replaced leaf
            leaves = self.nltk_tree.leaves()
            # print('new leaves', leaves)
            for leaf in leaves:
                if leaf == 'lexica_replaced_leaf':
                    leaf_index = leaves.index(leaf)
                    tree_position = self.nltk_tree.leaf_treeposition(leaf_index)
                    parent = tree_position[:-1]
                    del self.nltk_tree[parent]       # delete the merged subtrees
            return True

    def process_tree(self):
        """
        :param dic_layer: dictionary of the layer information in nltk_tree
        :return: nothing to return, directly modify the self.nltk tree obj
        """
        ls_leaf_pos = self.get_leaf_position()              # all leaf position
        dic_layer = self.generate_layer_dic(ls_leaf_pos)  # layer information in the tree
        height = self.nltk_tree.height()
        # loop through the tree from bottom up direction
        non_binary_detected = 0
        for i in range(0, height):
            layer_num = height - 1 - i
            # print('dealing with layer', layer_num)
            ls_layer = dic_layer[layer_num]
            ls_parent_position, ls_parent_multiple_position, ls_parent_single_position = self.find_layer_parent(layer_num, ls_layer)
            # print(ls_parent_multiple_position)
            # print(ls_parent_single_position)
            # print(ls_parent_position)
            if ls_parent_multiple_position:
                non_binary_detected = 1
                # print('target multiple parent found:', ls_parent_multiple_position)
                ls_parent_content = [str(self.nltk_tree[parent_position['parent']]) for parent_position in
                                     ls_parent_multiple_position]
                set_parent_content = set(ls_parent_content)
                if len(ls_parent_content) != len(set_parent_content):
                    return False
                for parent_multiple in ls_parent_multiple_position:
                    # print('current parent:', parent_multiple)
                    # for each parent, find its children
                    ls_children = []
                    tup_parent_position = parent_multiple['parent']
                    target_parent = self.nltk_tree[tup_parent_position]
                    # if a same layer contains multiple targets
                    # the children positions of the former one should be removed before process following trees
                    ls_remove_layer_node_index = []
                    for j in range(0, len(ls_layer)):
                        obtained_parent = self.nltk_tree[ls_layer[j]].parent()
                        # print('obtained parent', obtained_parent, 'current parent', target_parent)
                        if target_parent == obtained_parent:
                            ls_children.append(ls_layer[j])
                            ls_remove_layer_node_index.append(j)
                    ls_remove_layer_node_index.sort()
                    ls_remove_layer_node_index.reverse()
                    for index in ls_remove_layer_node_index:
                        del ls_layer[index]
                    self.tree_transformation(parent=parent_multiple, ls_pos_children=ls_children, type='multiple')
            if ls_parent_single_position:
                # print('target single parent found:', ls_parent_single_position)
                for parent_single in ls_parent_single_position:
                    self.tree_transformation(parent=parent_single, type='single')
            if ls_parent_position:
                pass
                # print('layer', layer_num, 'finished')
            else:
                continue
        return non_binary_detected

    def generate_flat_binary_tree(self):
        """
        :return: a lisp style binary tree string which is generated by the input.
                'BADTREE' which indicates the tree couldn't be transformed to binary correctly.
        """
        non_binary_detected = 1
        loop_limit = 1000
        loop_time = 0
        while non_binary_detected != 0:
            non_binary_detected = self.process_tree()      # nltk tree after transformation
            loop_time += 1
            if loop_time >= loop_limit:
                break
        # print('obtain final binary tree after', loop_time - 1, 'times loops')
        if self.nltk_tree is False:
            self.bad_tree = True
            self.str_flat_binary_tree = 'BADTREE'
            return

        is_irregular = False    # tag for non numeric node label
        for sub_tree in self.nltk_tree.subtrees():
            if not re.findall(r'\b[0-9]+\b', sub_tree.label(), flags=re.IGNORECASE):
                is_irregular = True
                print('irregular label detected, bad tree', self.str_tree)
                break
        if is_irregular:
            self.bad_tree = True
            self.str_flat_binary_tree = 'BADTREE'
            return

        splitted = str(self.nltk_tree).split()
        flat_tree = ' '.join(splitted)
        self.str_flat_binary_tree = flat_tree

    def get_str_flat_binary_tree(self):
        return self.str_flat_binary_tree

    # disable on server
    def draw_tree(self):
        draw_trees(self.nltk_tree)

