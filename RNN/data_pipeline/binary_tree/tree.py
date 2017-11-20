import random
UNK = 'UNK'
# This file contains the dataset in a useful way. We populate a list of
# Trees to train/test our Neural Nets such that each Tree contains any
# number of Node objects.

# The best way to get a feel for how these objects are used in the program is to drop pdb.set_trace() in a few places throughout the codebase
# to see how the trees are used.. look where loadtrees() is called etc..


class Node:  # a node in the tree
    def __init__(self, label, word=None):
        self.label = label
        self.word = word
        self.parent = None  # reference to parent
        self.left = None  # reference to left child
        self.right = None  # reference to right child
        # true if I am a leaf (could have probably derived this from if I have
        # a word)
        self.isLeaf = False
        # true if we have finished performing fowardprop on this node (note,
        # there are many ways to implement the recursion.. some might not
        # require this flag)


class Tree:
    def __init__(self, treeString, openChar='(', closeChar=')'):
        """
        called by loadTrees(dataSet='train') 
        trees = [Tree(l) for l in fid.readlines()]

        treeString: line in text file
        """
        tokens = []
        self.open = '('
        self.close = ')'
        tokens = list(treeString)
        self.bad_tree = False
        self.root = self.parse(tokens)
        self.lchild = self.root.left
        self.rchild = self.root.right
        # print('here')
        if self.bad_tree:
            print('a bad tree')
            print(treeString)
        else:
            pass
            # print('good tree')
        if not self.bad_tree:
            self.labels = self.get_labels(self.root)
            self.labels = [l-1 for l in self.labels]

    def get_labels(self, node):
        if node is None:
            return []
        return self.get_labels(node.left) + self.get_labels(node.right) + [node.label]

    def parse(self, tokens, parent=None):
        """
        turn char + ( or ) into node
        => recursively encode into an object in tree form***
        """
        # print 'tokens', tokens
        # Aaron 2017.11.16
        # do not really help with checking whether a tree is binary
        if tokens:
            if tokens[0] != self.open:
                self.bad_tree = True
                return
            if tokens[-1] != self.close:
                self.bad_tree = True
                return
        else:
            return
        # assert tokens[0] == self.open, "Malformed tree"
        # assert tokens[-1] == self.close, "Malformed tree"
        # split = 2  # position after open and label
        if tokens[2] == ' ':
            split = 3
        else:
            split = 4
        cnt_open = cnt_close = 0
        if tokens[split] == self.open:
            cnt_open += 1
            split += 1
        # Find where left child and right child split
        while cnt_open != cnt_close:
            if tokens[split] == self.open:
                cnt_open += 1
            if tokens[split] == self.close:
                cnt_close += 1
            split += 1
        # New node
        if tokens[2] == ' ':
            node = Node(int(tokens[1]))
            # print 'node label: ', node.label
        else:
            node = Node(int(tokens[1] + tokens[2]))  # tokens[1] or tokens[1]+tokens[2] fills label in Node
            # print 'node label: ', node.label
        # print "tokens[1]: ", tokens[1] # all the number label in one sentence
        node.parent = parent
        # leaf Node
        if cnt_open == 0:
            if tokens[2] == ' ':
                node.word = ''.join(tokens[3:-1]).lower()  # lower case?
            else:
                node.word = ''.join(tokens[4:-1]).lower()
            # print "node.word: ", node.word # e.g. director, do, if
            node.isLeaf = True
            # print(tokens)
            # print(node.word)
            # print('token above is leaf')
            # print(node)
            return node
        if tokens[2] == ' ':
            # print 'node left 3 split', tokens[3:split]
            node.left = self.parse(tokens[3:split], parent=node)
            # print(node.left)
        else:
            # print 'node left 4 split', tokens[4:split]
            node.left = self.parse(tokens[4:split], parent=node)
            # print(node.left)
        # print tokens[split+1:-1]
        # quit()
        # print 'node right', tokens[split+1:-1]
        node.right = self.parse(tokens[split + 1:-1], parent=node)
        return node