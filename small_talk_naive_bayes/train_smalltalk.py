from sklearn.naive_bayes import MultinomialNB
from collections import Counter

from chatbot_nlp_model.nlp_debugger_test.mysql_utils.db_manager import DBConn

import numpy as np
import pickle
import string
import re


class SmallTalkTrain(object):

    def __init__(self):
        self.log = print
        self.labels = []
        self.msgs = []
        self.translator = str.maketrans('', '', string.punctuation)
        self.ls_bag_of_words = []

    def load_data(self):
        with open('chatbot_nlp_model/ml_training/small_talk/labelled_data/label.txt', 'r') as label_file:
            labels = label_file.readlines()
            self.labels = [label.strip() for label in labels]

        with open('chatbot_nlp_model/ml_training/small_talk/labelled_data/msg.txt', 'r') as msg_file:
            msgs = msg_file.readlines()
            self.msgs = [msg.strip().replace("\'", "'").translate(self.translator) for msg in msgs]
            for i in range(0, len(self.msgs)):
                self.msgs[i] = re.sub(r'[\u4e00-\u9fff]+', ' ', self.msgs[i])

    def generate_bag_of_word(self):
        word_set = set()
        for msg in self.msgs:
            ls_bag_of_words = msg.lower().split(' ')
            for word in ls_bag_of_words:
                if word != '':
                    word_set.add(word)
        self.ls_bag_of_words = list(word_set)

    def generate_matrix(self):
        dic_word_small = {dic: 0 for dic in self.ls_bag_of_words}
        dic_word_non_small = {dic: 0 for dic in self.ls_bag_of_words}
        if len(self.msgs) == len(self.labels):
            for i in range(0, len(self.msgs)):
                ls_bag_of_words = self.msgs[i].lower().split(' ')
                for word in ls_bag_of_words:
                    if word != '':
                        if self.labels[i] == 'small':
                            dic_word_small[word] += 1
                        else:
                            dic_word_non_small[word] += 1

        ls_small = []
        ls_nonsmall = []

        for key in dic_word_small:
            ls_small.append(dic_word_small[key])
        for key in dic_word_non_small:
            ls_nonsmall.append(dic_word_non_small[key])

        matrix = [ls_small, ls_nonsmall]
        return matrix

    def generate_matrix_new(self):
        ls_small = []
        ls_nonsmall = []
        ls_label_small = []
        ls_label_nonsmall = []
        i = 0
        if len(self.msgs) == len(self.labels):
            for i in range(0, len(self.msgs)):
                # if i == 10:
                #     break
                # i += 1
                ls_bag_of_words = self.msgs[i].lower().split(' ')
                if self.labels[i] == 'small':
                    dic_word_small = {dic: 0 for dic in self.ls_bag_of_words}
                    ls_word = []
                    for word in ls_bag_of_words:
                        if word != '':
                            dic_word_small[word] += 1
                    for key in dic_word_small:
                        ls_word.append(dic_word_small[key])
                    ls_small.append(ls_word)
                    ls_label_small.append(0)
                else:
                    dic_word_non_small = {dic: 0 for dic in self.ls_bag_of_words}
                    for word in ls_bag_of_words:
                        if word != '':
                            dic_word_non_small[word] += 1
                    for key in dic_word_non_small:
                        ls_word.append(dic_word_non_small[key])
                    ls_nonsmall.append(ls_word)
                    ls_label_nonsmall.append(1)
        # print(ls_small)
        matrix = [ls_small, ls_nonsmall]
        matrix_label = [ls_label_small, ls_label_nonsmall]
        return [matrix, matrix_label]

    def train(self):
        matrix_result = self.generate_matrix_new()
        matrix = matrix_result[0]
        matrix_label = matrix_result[1]
        clf = MultinomialNB()
        print("before training the model")
        clf.fit(matrix, matrix_label)
        print("after training the model")
        db_conn = DBConn()

        with open('chatbot_nlp_model/ml_training/small_talk/models/small_talk.pkl', 'wb') as f:
            pickle.dump(clf, f)

        sql = 'select id, msg_slot from nlp_debugger_test_result'
        sql_upd = 'update nlp_debugger_test_result set classifier = %s where id = %s'

        result = db_conn.fetch_data(sql, [])

        # result = [{'msg_slot': ' say thanks'}]
        for msg in result:
            dic_predict = {dic: 0 for dic in self.ls_bag_of_words}
            msg_id = msg['id']
            message = msg['msg_slot']
            # message = 'hi'
            message = re.sub(r'[\u4e00-\u9fff]+', ' ', message).lower().translate(self.translator).strip().split(' ')
            # print(message)
            for word in message:
                # print(word)
                if word != '':
                    if word in dic_predict.keys():
                        dic_predict[word] += 1
            ls_predict = []
            for key in dic_predict:
                ls_predict.append(dic_predict[key])
            # print(ls_predict)
            result = clf.predict([ls_predict])
            # print(result[0])
            db_conn.update_data(sql_upd, [result[0], msg_id])
