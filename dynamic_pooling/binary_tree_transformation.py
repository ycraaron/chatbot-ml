from stanfordnlp.stanford_connector import stanford_tree
from nltk.parse import stanford
from nltk.tree import Tree
from nltk.tree import ParentedTree
from nltk.draw.tree import draw_trees
from timeit import default_timer as timer
import re
import sys

class BinaryTree(object):

    def __init__(self, nltk_tree):
        self.nltk_tree = nltk_tree

    def get_stanford_tree(self, msg):
        raw_result = stanford_tree(msg)
        lisp_tree = raw_result['sentences'][0]['parse']
        return lisp_tree


    # deprecated since there were some misunderstandings at the beginning
    # use it only when you want to add a null leaf to every leaf parent to make them binary.
    def add_leaves(self, nltk_tree):
        ls_leaves = nltk_tree.leaves()
        ls_leaf_indices = [ls_leaves.index(leaf) for leaf in ls_leaves]
        for i in range(0, len(ls_leaf_indices)):
            leaf_tree_location = nltk_tree.leaf_treeposition(ls_leaf_indices[i])
            parent_position = leaf_tree_location[:-1]
            nltk_tree[parent_position].append('@@')
            for j in range(i, len(ls_leaf_indices)):
                ls_leaf_indices[j] += 1
        return nltk_tree


def get_stanford_tree(msg):
    raw_result = stanford_tree(msg)
    lisp_tree = raw_result['sentences'][0]['parse']
    return lisp_tree


# get all the leaves
def get_leaf_position(nltk_tree):
    ls_leaves = nltk_tree.leaves()
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
        leaf_tree_location = nltk_tree.leaf_treeposition(leaf)
        ls_leaf_position.append(leaf_tree_location)
    return ls_leaf_position


def get_inner_nodes(nltk_tree):
    return nltk_tree


def load_trees(tree_file='trees/wiki_09_tree_out.txt'):
    file = tree_file
    with open(file, 'rb') as fid_tree:
        ls_trees = [l.decode('utf-8') for l in fid_tree.readlines()]
    return ls_trees


def build_nltk_tree(str_tree):
    nltk_tree_obj = ParentedTree.fromstring(str_tree)
    return nltk_tree_obj


def find_max_children(nltk_tree):
    set_position = set()
    cnt_all = 0
    cnt_4 = 0
    cnt_10 = 0
    tree_positions = nltk_tree.treepositions()
    for position in tree_positions:
        for index in position:
            if index > 4:
                return True

    # for tree in load_trees():
    #     nltk_tree = build_nltk_tree(tree)
    #     tree_positions = nltk_tree.treepositions()
    #     for position in tree_positions:
    #         for index in position:
    #             if index > 1:
    #                 set_position.add(index)
    #             # if index == 5:
    #             #     print(tree)
    #             #     quit()
    #             if index in range(5, 11):
    #                 cnt_4 += 1
    #             if index > 10:
    #                 cnt_10 += 1
    #             if index > 40:
    #                 print(tree)
    #                 print(tree_positions)
    #             if index < 5:
    #                 cnt_all += 1
    #
    # print('total: ', cnt_all)
    # print('more than 4: ', cnt_4)
    # print('more than 10: ', cnt_10)
    # print(set_position)
    # print(max(set_position))


# generate the layer information of a tree
# pruning all the leaves
def generate_layer_dic(nltk_tree, leaves):
    ls_tree_position = nltk_tree.treepositions()
    height = nltk_tree.height()
    dic_tree = {}
    for i in range(0, height):
        dic_tree[i] = []
    # print(dic_tree)
    for position in ls_tree_position:
        if position not in leaves:
            dic_tree[len(position)].append(position)
    # print(dic_tree)
    return dic_tree


def find_layer_parent(layer, ls_layer):
    if ls_layer and layer > 1:
        ls_layer_parent = []
        ls_layer_parent_multiple = [] # store the parent with more than two children
        ls_layer_parent_single = [] # store the parent with single child
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
                    # last element in tuple represents the num of children e.g: the parent of node (0, 2, 1, 3, 3) has at least 4 children
                    cnt_child = child_node_position[len(child_node_position) - 1]
                    if cnt_child > max_child_num:
                        max_child_num = cnt_child
            if max_child_num == 0:
                # print('target single parent found:', parent)
                ls_layer_parent_single.append(parent)
            if max_child_num > 1:
                # print('target multiple parent found:', parent)
                ls_layer_parent_multiple.append({'parent': parent, 'max': max_child_num})

        return ls_layer_parent, ls_layer_parent_multiple, ls_layer_parent_single
    else:
        print('empty layer:', layer)
        return [], [], []


def tree_transformation(nltk_tree, parent, ls_pos_children=[], type=''):
    if type == 'single':
        print('single tree component')
        print(nltk_tree[parent])
        nltk_tree[parent].append(ParentedTree(nltk_tree[parent].label(), ['@@']))
        # print(nltk_tree[parent])
    elif type == 'multiple':
        print('multiple tree component')
        tup_position_parent = parent['parent']
        tree_parent = nltk_tree[tup_position_parent]
        cnt_children = parent['max']
        cnt_sub_tree_pair = int((cnt_children + 1) / 2)
        remainder = (cnt_children + 1) % 2
        print('num of tree pair:', cnt_sub_tree_pair)
        print('all children position for multiple tree:', ls_pos_children)
        for i in range(0, cnt_sub_tree_pair):
            pos_tree1 = ls_pos_children[2*i]
            pos_tree2 = ls_pos_children[2*i+1]
            tree1 = nltk_tree[pos_tree1]
            tree2 = nltk_tree[pos_tree2]
            # print('parent:', tree_parent)
            # print('tree 1:', tree1)
            # print('tree 2:', tree2)
            # draw_trees(tree1)
            # new_tree = ParentedTree()
            label_parent = tree_parent.label()
            # for subtree in tree_parent.subtrees():
            #     print('sub')
            #     print(subtree)
            str_tree1 = str(tree1)
            str_tree2 = str(tree2)
            tree_parent.append(ParentedTree(label_parent, [ParentedTree.fromstring(str_tree1), ParentedTree.fromstring(str_tree2)]))

        # print(ls_pos_children[:-1])
        # print(ls_pos_children)
        # draw_trees(nltk_tree)
        # quit()
        if remainder != 0:
            pos_remaining_child = ls_pos_children[len(ls_pos_children) - 1]
            tree_remaining = nltk_tree[pos_remaining_child]
            print('remaining tree', tree_remaining)
            tree_parent.append(tree_remaining.copy(deep=True))

        for child in ls_pos_children:
            print(nltk_tree[child], 'will be replaced')
            nltk_tree[child] = ParentedTree('LEXICA_REPLACED', ['lexica_replaced_leaf'])

        # draw_trees(nltk_tree)
        # remove the replaced leaf
        leaves = nltk_tree.leaves()
        print('new leaves', leaves)
        for leaf in leaves:
            if leaf == 'lexica_replaced_leaf':
                leaf_index = leaves.index(leaf)
                tree_position = nltk_tree.leaf_treeposition(leaf_index)
                # print('pos', tree_position)
                parent = tree_position[:-1]
                # print('parent', parent)
                del nltk_tree[parent]

        # print(nltk_tree)
        # draw_trees(nltk_tree)
        # quit()
        print(nltk_tree[tup_position_parent])

    return nltk_tree


def process_tree(nltk_tree, dic_layer):
    height = nltk_tree.height()
    print('height', height)
    # loop through the tree from bottom up direction
    for i in range(0, height):
        layer_num = height-1-i
        print('dealing with layer:', layer_num)
        ls_layer = dic_layer[layer_num]
        # print(ls_layer)
        ls_parent_position, ls_parent_multiple_position, ls_parent_single_position = find_layer_parent(layer_num, ls_layer)
        if ls_parent_multiple_position:
            print('target multiple parent found:', ls_parent_multiple_position)
            ls_parent_content = [str(nltk_tree[parent_position['parent']]) for parent_position in ls_parent_multiple_position]
            set_parent_content = set(ls_parent_content)
            if len(ls_parent_content) != len(set_parent_content):
                return False
            for parent_multiple in ls_parent_multiple_position:
                # print('current parent:', parent_multiple)
                # for each parent, find its children
                ls_children = []
                tup_parent_position = parent_multiple['parent']
                target_parent = nltk_tree[tup_parent_position]
                print('ls_layer in each loop', ls_layer)
                # if a same layer contains multiple targets, modified position should be removed before process next tree
                ls_remove_layer_node_index = []
                for j in range(0, len(ls_layer)):
                    obtained_parent = nltk_tree[ls_layer[j]].parent()
                    # print('obtained parent', obtained_parent, 'current parent', target_parent)
                    if target_parent == obtained_parent:
                        ls_children.append(ls_layer[j])
                        ls_remove_layer_node_index.append(j)
                ls_remove_layer_node_index.sort()
                ls_remove_layer_node_index.reverse()
                for index in ls_remove_layer_node_index:
                    del ls_layer[index]
                print('layer_remaining nodes:', ls_layer)
                # for pos_child in ls_layer:
                #     obtained_parent = nltk_tree[pos_child].parent()
                #     if target_parent == obtained_parent:
                #         # print("found found found")
                #         ls_children.append(pos_child)
                # draw_trees(nltk_tree)
                nltk_tree = tree_transformation(nltk_tree=nltk_tree, parent=parent_multiple, ls_pos_children=ls_children, type='multiple')
        if ls_parent_single_position:
            print('target single parent found:', ls_parent_single_position)
            for parent_single in ls_parent_single_position:
                nltk_tree = tree_transformation(nltk_tree=nltk_tree, parent=parent_single,  type='single')
        if ls_parent_position:
            print('layer', layer_num, 'finished')
        else:
            continue
    return nltk_tree


def single_tree_test(tree_str):
    msg = 'the fighting renegade the fighting renegade is a American western consititution'
    lisp_tree = tree_str
    # lisp_tree = get_stanford_tree(msg)
    lisp_tree = '(1 (1 (1 (1 (1 (14 (14 (40 Adults) @@) (16 (33 in) (14 (14 (30 the) (34 Olivella)) (40 species)))) (22 (22 (58 are) (8 (47 usually) @@)) (7 (47 quite) (34 small)))) (8 (47 hence) @@)) (1 (14 (30 the) (39 genus)) (22 (59 has) (14 (14 (14 (30 the) (34 common)) (39 name)) (2 (1 (14 (14 (39 dwarf) (40 olive.Species)) (16 (33 of) (14 (41 Oliva) @@))) (22 (22 (58 are) (8 (47 usually) @@)) (7 (35 larger) @@))) @@))))) (28 but)) (1 (14 (31 there) @@) (22 (58 are) (14 (40 exceptions) @@))))'
    lisp_tree = '(1 (1 (14 (14 (14 (30 The) (41 United)) (42 States)) (20 (14 (14 (40 delegates) (14 @@)) (16 (33 in) (14 (41 Miss) (41 Earth)))) (16 (33 from) (16 @@)))) (: --)) (22 (55 were) (22 (57 selected) (16 (33 by) (14 (14 (14 (30 the) (41 Miss)) (14 (41 America) (41 International)) (39 pageant)) (2 (24 (63 where) (24 @@)) (1 (14 (30 the) (39 prize)) (22 (55 was) (1 (22 (52 to) (22 (22 (54 represent) (14 (14 (30 the) (41 United)) (42 States))) (16 (33 at) (14 (14 (30 the) (41 Miss)) (14 (41 Earth) (39 Pageant)))))) (1 @@))))))))))'
    # print(lisp_tree)
    nltk_tree_obj = ParentedTree.fromstring(lisp_tree)
    # draw_trees(nltk_tree_obj)
    # for sub_tree in nltk_tree_obj.subtrees():
    #     if sub_tree.label() == ':':
    #         sub_tree.set_label('999')
    # draw_trees(nltk_tree_obj)
    # quit()
    ls_leaf_pos = get_leaf_position(nltk_tree_obj)
    print('leaves:', ls_leaf_pos)
    print(len(ls_leaf_pos))
    dic_layer = generate_layer_dic(nltk_tree_obj, ls_leaf_pos)
    print('layer infomation:', dic_layer)
    nltk_tree_obj = process_tree(nltk_tree_obj, dic_layer)
    # print(nltk_tree_obj)
    draw_trees(nltk_tree_obj)


# 1. find all leaves and add sibling node -> Deprecated
# 2. find all inner nodes with single child or more than 2 children -> DONE
# 3. deal with those inner nodes -> Done
def entry():
    # find_max_children()
    msg = 'xx may be concave or have deep furrows or have others'
    # msg = ''
    # tree_file = sys.argv[1]
    ls_lisp_tree = load_trees('trees/out_put_tree_corpus.txt')
    # ls_lisp_tree = load_trees(tree_file)
    print(len(ls_lisp_tree))
    ls_remove_index = []
    excep = 0
    for i in range(0, len(ls_lisp_tree)):
        try:
            if find_max_children(ParentedTree.fromstring(ls_lisp_tree[i])):
                ls_remove_index.append(i)
        except Exception:
            excep += 1
            ls_remove_index.append(i)

    ls_remove_index.sort()
    ls_remove_index.reverse()
    print('number of exceps', excep)
    for index in ls_remove_index:
        del ls_lisp_tree[index]

    print(len(ls_lisp_tree))
    # quit()

    # lisp_tree = get_stanford_tree(msg)
    # print(lisp_tree)
    # lisp_tree = '(ROOT   (S     (NP (NN xx @@) @@)     (VP       (VP (VP (MD may @@)         (VP (VB be @@)           (ADJP (JJ concave @@) @@)))       (CC or @@))       (VP (VBP have @@)         (VP           (ADVP (JJ deep @@) @@)           (VBZ furrows @@))))))'
    # lisp_tree = '( 0 ( 1 ( 16 ( 33 Besides ) ( 14 ( 30 the ) ( 34 common ) ( 40 minerals ) ( 39 quartz ) ) )  ( 14 ( 14 ( 34 alkali ) ( 39 feldspar )  ( 39 plagioclase )  ( 39 biotite )  ( 39 muscovite ) ) ( 9 ( 47 as ) ( 47 well ) ( 33 as ) ) ( 14 ( 14 ( 39 calcite )  ( 39 dolomite ) ( 28 and ) ( 39 gypsum ) ) ( 14 ( 35 rarer ) ( 40 minerals ) ) ) ) ( 22 ( 58 occur )  ( 16 ( 33 for ) ( 14 ( 14 ( 39 example ) ( 39 actinolite ) )  ( 14 ( 39 allanite )  ( 39 andalusite )  ( 39 antigorite )  ( 39 apatite )  ( 39 arsenopyrite )  ( 39 baryte )  ( 39 cassiterite )  ( 39 chalcedony )  ( 39 chalcopyrite )  ( 39 chlorite )  ( 39 chromite )  ( 39 clinopyroxene )  ( 39 chrysotile )  ( 39 cordierite )  ( 39 cyanite )  ( 39 epidote )  ( 39 galena )  ( 39 garnet )  ( 39 goethite )  ( 39 graphite )  ( 39 hematite )  ( 39 hornblende )  ( 39 ilmenite )  ( 39 kaolinite )  ( 39 limonite )  ( 39 magnetite )  ( 39 manganite )  ( 39 marcasite )  ( 39 montmorillonite )  ( 39 prehnite )  ( 39 psilomelane )  ( 39 pyrite )  ( 39 pyrolusite )  ( 39 pyrrhotite )  ( 39 rutile )  ( 39 sillimanite )  ( 39 sphalerite )  ( 39 sphene )  ( 39 staurolite )  ( 39 tourmaline ) ( 28 and ) ( 39 zircon ) ) ) ) )  ) )'
    # lisp_tree = '(4 (3 (2 If) (3 (2 you) (3 (2 sometimes) (2 (2 like) (3 (2 to) (3 (3 (2 go) (2 (2 to) (2 (2 the) (2 movies)))) (3 (2 to) (3 (2 have) (4 fun))))))))) (2 (2 ,) (2 (2 Wasabi) (3 (3 (2 is) (2 (2 a) (2 (3 good) (2 (2 place) (2 (2 to) (2 start)))))) (2 .)))))'
    fid_binary_out = open('trees/binary_tree_out.txt', 'wb')
    start = timer()
    i = 0
    # print(ls_lisp_tree[0])
    # single_tree_test(ls_lisp_tree[0])
    cnt_duplicate = 0
    cnt_irregular = 0
    for lisp_tree in ls_lisp_tree:
        is_irregular = False
        nltk_tree_obj = ParentedTree.fromstring(lisp_tree)
        ls_leaf_pos = get_leaf_position(nltk_tree_obj)
        dic_layer = generate_layer_dic(nltk_tree_obj, ls_leaf_pos)
        nltk_tree_obj = process_tree(nltk_tree_obj, dic_layer)
        # draw_trees(nltk_tree_obj)
        # draw_trees(nltk_tree_obj)
        if nltk_tree_obj is False:
            cnt_duplicate += 1
            continue
        for sub_tree in nltk_tree_obj.subtrees():
            if not re.findall(r'\b[0-9]+\b', sub_tree.label()):
                cnt_irregular += 1
                is_irregular = True
                break
        if is_irregular:
            continue
        nltk_tree_obj = nltk_tree_obj.pop()
        splitted = str(nltk_tree_obj).split()
        flat_tree = ' '.join(splitted)
        # print(flat_tree)
        fid_binary_out.write(flat_tree.encode('utf-8'))
        fid_binary_out.write('\n'.encode('utf-8'))
    print('duplication situation:', cnt_duplicate)
    print('irregular situation:', cnt_irregular)
    end = timer()
    print(end-start)
    quit()


def test():
    tree_str = '(1 (1 (14 (14 (14 (30 The) (41 United)) (42 States)) (20 (14 (14 (40 delegates) (14 @@)) (16 (33 in) (14 (41 Miss) (41 Earth)))) (16 (33 from) (16 @@)))) (: --)) (22 (55 were) (22 (57 selected) (16 (33 by) (14 (14 (14 (30 the) (41 Miss)) (14 (41 America) (41 International)) (39 pageant)) (2 (24 (63 where) (24 @@)) (1 (14 (30 the) (39 prize)) (22 (55 was) (1 (22 (52 to) (22 (22 (54 represent) (14 (14 (30 the) (41 United)) (42 States))) (16 (33 at) (14 (14 (30 the) (41 Miss)) (14 (41 Earth) (39 Pageant)))))) (1 @@))))))))))'
    nltk_tree = ParentedTree.fromstring(tree_str)
    for sub in nltk_tree.subtrees():
        if not re.findall(r'\b[0-9]+\b', sub.label()):
            print(sub.label())

# test()
entry()
