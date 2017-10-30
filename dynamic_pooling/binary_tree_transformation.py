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


def get_leaf_position(nltk_tree):
    ls_leaves = nltk_tree.leaves()
    ls_leaf_indices = [ls_leaves.index(leaf) for leaf in ls_leaves]
    ls_leaf_position = []
    for leaf in ls_leaf_indices:
        leaf_tree_location = nltk_tree.leaf_treeposition(leaf)
        ls_leaf_position.append(leaf_tree_location)
    return ls_leaf_position


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
                    child_num = child_node_position[len(child_node_position) - 1]
                    if child_num > max_child_num:
                        max_child_num = child_num
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
        nltk_tree[parent].append('@@')
        print(nltk_tree[parent])
    elif type == 'multiple':
        print('multiple tree component')
        tup_position_parent = parent['parent']
        tree_parent = nltk_tree[tup_position_parent]
        cnt_children = parent['max']
        cnt_sub_tree_pair = int((cnt_children + 1) / 2)
        remainder = (cnt_children + 1) % 2

        print('num of tree pair:', cnt_sub_tree_pair)
        for i in range(0, cnt_sub_tree_pair):
            pos_tree1 = ls_pos_children[2*i]
            pos_tree2 = ls_pos_children[2*i+1]
            tree1 = nltk_tree[pos_tree1]
            tree2 = nltk_tree[pos_tree2]
            print('parent:', tree_parent)
            print('tree 1:', tree1)
            print('tree 2:', tree2)
            # draw_trees(tree1)
            # new_tree = ParentedTree()
            label_parent = tree_parent.label()
            # for subtree in tree_parent.subtrees():
            #     print('sub')
            #     print(subtree)
            str_tree1 = str(tree1)
            str_tree2 = str(tree2)
            tree_parent.append(ParentedTree(label_parent, [ParentedTree.fromstring(str_tree1), ParentedTree.fromstring(str_tree2)]))
            # tree_parent[0].insert(0, ParentedTree.fromstring(str_tree1))
            # new_sub_tree = tree_parent[0]
            # print('new sub tree:', new_sub_tree)
            # draw_trees(nltk_tree)
            # tree_parent.insert(0, ParentedTree(label_parent, children=[tree1]))
            # quit()
            # tree_parent[0].append(tree1)
            # tree_parent[0].append(tree2)

        print(ls_pos_children[:-1])
        print(ls_pos_children)
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

        leaves = nltk_tree.leaves()
        for leaf in leaves:
            if leaf == 'lexica_replaced_leaf':
                leaf_index = leaves.index(leaf)
                tree_position = nltk_tree.leaf_treeposition(leaf_index)
                print('pos', tree_position)
                parent = tree_position[:-1]
                print('parent', parent)
                del nltk_tree[parent]

        print(nltk_tree)
        print(leaves)
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
            for parent_multiple in ls_parent_multiple_position:
                # for each parent, find its children
                ls_children = []
                tup_parent_position = parent_multiple['parent']
                target_parent = nltk_tree[tup_parent_position]
                for pos_child in ls_layer:
                    obtained_parent = nltk_tree[pos_child].parent()
                    if target_parent == obtained_parent:
                        # print("found found found")
                        ls_children.append(pos_child)

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


# 1. find all leaves and add sibling node -> DONE
# 2. find all inner nodes with more than 2 children -> DONE
# 3. deal with those inner nodes
def entry():
    # find_max_children()
    msg = 'xx may be concave or have deep furrows'
    lisp_tree = get_stanford_tree(msg)
    # lisp_tree = '(ROOT   (S     (NP (NN xx @@) @@)     (VP       (VP (VP (MD may @@)         (VP (VB be @@)           (ADJP (JJ concave @@) @@)))       (CC or @@))       (VP (VBP have @@)         (VP           (ADVP (JJ deep @@) @@)           (VBZ furrows @@))))))'
    # lisp_tree = '( 0 ( 1 ( 16 ( 33 Besides ) ( 14 ( 30 the ) ( 34 common ) ( 40 minerals ) ( 39 quartz ) ) )  ( 14 ( 14 ( 34 alkali ) ( 39 feldspar )  ( 39 plagioclase )  ( 39 biotite )  ( 39 muscovite ) ) ( 9 ( 47 as ) ( 47 well ) ( 33 as ) ) ( 14 ( 14 ( 39 calcite )  ( 39 dolomite ) ( 28 and ) ( 39 gypsum ) ) ( 14 ( 35 rarer ) ( 40 minerals ) ) ) ) ( 22 ( 58 occur )  ( 16 ( 33 for ) ( 14 ( 14 ( 39 example ) ( 39 actinolite ) )  ( 14 ( 39 allanite )  ( 39 andalusite )  ( 39 antigorite )  ( 39 apatite )  ( 39 arsenopyrite )  ( 39 baryte )  ( 39 cassiterite )  ( 39 chalcedony )  ( 39 chalcopyrite )  ( 39 chlorite )  ( 39 chromite )  ( 39 clinopyroxene )  ( 39 chrysotile )  ( 39 cordierite )  ( 39 cyanite )  ( 39 epidote )  ( 39 galena )  ( 39 garnet )  ( 39 goethite )  ( 39 graphite )  ( 39 hematite )  ( 39 hornblende )  ( 39 ilmenite )  ( 39 kaolinite )  ( 39 limonite )  ( 39 magnetite )  ( 39 manganite )  ( 39 marcasite )  ( 39 montmorillonite )  ( 39 prehnite )  ( 39 psilomelane )  ( 39 pyrite )  ( 39 pyrolusite )  ( 39 pyrrhotite )  ( 39 rutile )  ( 39 sillimanite )  ( 39 sphalerite )  ( 39 sphene )  ( 39 staurolite )  ( 39 tourmaline ) ( 28 and ) ( 39 zircon ) ) ) ) )  ) )'
    nltk_tree_obj = ParentedTree.fromstring(lisp_tree)

    ls_leaf_pos = get_leaf_position(nltk_tree_obj)
    print('leaves:', ls_leaf_pos)
    dic_layer = generate_layer_dic(nltk_tree_obj, ls_leaf_pos)
    nltk_tree_obj = process_tree(nltk_tree_obj, dic_layer)
    draw_trees(nltk_tree_obj)

entry()
