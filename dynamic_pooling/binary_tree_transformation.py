from stanfordnlp.stanford_connector import stanford_tree
from nltk.parse import stanford
from nltk.tree import Tree
from nltk.tree import ParentedTree
from nltk.draw.tree import draw_trees


def get_stanford_tree(msg):
    raw_result = stanford_tree(msg)
    lisp_tree = raw_result['sentences'][0]['parse']
    return lisp_tree


def add_leaves(nltk_tree):
    ls_leaves = nltk_tree.leaves()
    ls_leaf_indices = [ls_leaves.index(leaf) for leaf in ls_leaves]
    for i in range(0, len(ls_leaf_indices)):
        leaf_tree_location = nltk_tree.leaf_treeposition(ls_leaf_indices[i])
        parent_position = leaf_tree_location[:-1]
        nltk_tree[parent_position].append('@@')
        for j in range(i, len(ls_leaf_indices)):
            ls_leaf_indices[j] += 1
    return nltk_tree


def get_inner_nodes(nltk_tree):
    return nltk_tree


def load_trees():
    file = 'trees/wiki_09_tree_out.txt'
    with open(file, 'rb') as fid_tree:
        ls_trees = [l.decode('utf-8') for l in fid_tree.readlines()]
    return ls_trees


def build_nltk_tree(str_tree):
    nltk_tree_obj = ParentedTree.fromstring(str_tree)
    return nltk_tree_obj


def find_max_children():
    set_position = set()
    cnt_all = 0
    cnt_4 = 0
    cnt_10 = 0
    for tree in load_trees():
        nltk_tree = build_nltk_tree(tree)
        tree_positions = nltk_tree.treepositions()
        for position in tree_positions:
            for index in position:
                if index > 1:
                    set_position.add(index)
                # if index == 5:
                #     print(tree)
                #     quit()
                if index in range(5, 11):
                    cnt_4 += 1
                if index > 10:
                    cnt_10 += 1
                if index > 40:
                    print(tree)
                    print(tree_positions)
                if index < 5:
                    cnt_all += 1

    print('total: ', cnt_all)
    print('more than 4: ', cnt_4)
    print('more than 10: ', cnt_10)
    print(set_position)
    print(max(set_position))


def process_tree():

# 1. find all leaves and add sibling node -> DONE
# 2. find all inner nodes with more than 2 children -> DONE
# 3. deal with those inner nodes
def entry():
    # find_max_children()
    msg = 'xx may be concave or have deep furrows'
    lisp_tree = get_stanford_tree(msg)
    # lisp_tree = '(ROOT   (S     (NP (NN xx @@) @@)     (VP       (VP (VP (MD may @@)         (VP (VB be @@)           (ADJP (JJ concave @@) @@)))       (CC or @@))       (VP (VBP have @@)         (VP           (ADVP (JJ deep @@) @@)           (VBZ furrows @@))))))'
    nltk_tree_obj = ParentedTree.fromstring(lisp_tree)

    print('height = ', nltk_tree_obj.height())
    tree_positions = nltk_tree_obj.treepositions()

    for position in tree_positions:
        print(position)
        print(len(position))

    draw_trees(nltk_tree_obj)

entry()
