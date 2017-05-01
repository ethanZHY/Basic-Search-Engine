'''
This model calculate documents' BM25 score for a query
And do the search function, rank the top documents by BM25 score given a query
'''

import math
from src.PseudoRelevenceFeedbackModel import PseudoRelevanceFeedbackModel
from src.Tokenizer import Tokenizer


class BM25RetrievalModel:
    uni_gram_inverted_list = dict()         # store inverted list
    doc_length = dict()                     # store each document's length
    k_1 = 0
    b = 0
    k_2 = 0
    result_id_list = list()
    corpus_path = ''
    '''
        initialze the Class with the path of the inverted list and the doc_length file generated from indexer
        inverted_lists and doc_length HashMap's keys are documentID in format: 'CACM-XXXX.Txt'
        '''
    def __init__(self, inverted_list_path, doc_length_path, corpus_path):
        self.uni_gram_inverted_list = dict()  # store inverted list
        self.doc_length = dict()  # store each document's length
        self.result_id_list = list()
        self.corpus_path = ''
        self.b = 0
        self.k_2 = 0
        self.k_1 = 0
        # read document length:
        self.corpus_path = corpus_path
        fw1 = open(doc_length_path, 'r', encoding='utf-8')
        for line in fw1.readlines():
            doc_id = line[:line.find(' ')]
            freq = line[line.find(' ')+1: line.rfind('\n')]
            self.doc_length.update({doc_id: freq})
        fw1.close()
        # read inverted list:
        fw1 = open(inverted_list_path, 'r', encoding='utf-8')
        for line in fw1.readlines():
            term = line[:line.find(' ')]
            line = line[line.find(' ')+1:]
            index = dict()
            lists = line.split(', ')
            for l in lists:
                if l.find('\n') != -1:
                    l = l[:l.find('\n')]
                doc_id = l[l.find("'")+1:l.find(':')-1]
                if l.find('}') != -1:
                    freq = l[l.find(':')+2:l.find('}')]
                else:
                    freq = l[l.find(':')+2:]
                index.update({doc_id: freq})
                self.uni_gram_inverted_list.update({term: index})

    def get_inverted_index(self):
        return self.uni_gram_inverted_list

    def get_doc_length(self):
        return self.doc_length

    # calculate corpus's average document length
    def get_average_doc_length(self):
        total_length = 0
        num_of_doc = 0
        for doc in self.doc_length.keys():
            num_of_doc += 1
            total_length += int(self.doc_length.get(doc))
        return total_length/num_of_doc

    '''
    search result based on query, num variable is the number of results shown
    run_feedback is the flag to control whether or not to run pseudo relevance feedback
    method returns a list of results
    '''
    def search(self, query, num, run_feedback):
        self.result_id_list = list()
        score_dict = self.calculate_BM25_score(query)
        # sort the result, and display top num's result in format:
        # query_id Q0 doc_id rank BM25_score system_name
        sorted_result = sorted(score_dict.items(), key=lambda d: d[1], reverse=True)
        line_buffer = list()
        for i in range(0, num):
            sorted_result[i] = str(sorted_result[i])
            doc_id = sorted_result[i][sorted_result[i].find('(')+1:sorted_result[i].find(' ')-1]
            score = sorted_result[i][sorted_result[i].find(' ')+1:sorted_result[i].find(')')]
            line = 'Q0 '+doc_id+' '+score
            self.result_id_list.append(doc_id[doc_id.find("'")+1:doc_id.rfind("'")])
            line_buffer.append(line)
        query_tokenize = Tokenizer()
        query = query_tokenize.remove_punctuation(query)
        # True to run pseudo relevance feedback
        if run_feedback is True:
            line_buffer = self.run_feedback(query)
        # self.save_result(query, line_buffer)
        return line_buffer

    def calculate_BM25_score(self, query):
        average_len = self.get_average_doc_length()
        N = len(self.doc_length.keys())         # total document number
        score_dict = dict()  # store each document's BM25 score
        query_list = str(query).split(' ')  # split query into uni-gram
        query_freq = dict()  # store each term's frequency in the query
        # calculate term frequency
        for term in query_list:
            if term not in query_freq:
                query_freq.update({term: 1})
            else:
                query_freq.update(({term: query_freq.get(term) + 1}))
        # calculate each document's BM25 score; r = R = 0 since assume no relevance information given
        for doc in self.doc_length.keys():
            doc_len = int(self.doc_length.get(doc))     # get dl
            K = self.k_1 * ((1 - self.b) + self.b * doc_len / average_len)  # calculate K
            bm_25_score = 0
            # add each term's value together
            for term in query_freq.keys():
                f_i = 0
                if term in self.uni_gram_inverted_list.keys():
                    n_i = len(self.uni_gram_inverted_list.get(term).keys())     # term occurrence in total documents
                    if doc in self.uni_gram_inverted_list.get(term).keys():
                        f_i = float(self.uni_gram_inverted_list.get(term).get(doc))     # term occurrence in one doc
                    else:
                        f_i = 0     # if term does not exist in this document
                else:
                    n_i = 0         # if term never appear in corpus
                q_f = float(query_freq.get(term))       # term frequency
                bm_25_score += math.log10(1/((n_i+0.5)/(N-n_i+0.5))) * ((self.k_1+1)*f_i)/(K+f_i) * \
                               ((self.k_2+1)*q_f)/(self.k_2+q_f)
            score_dict.update({doc: bm_25_score})  # store each document's score
        return score_dict

    '''
       method to run pseudo relevance feedback on given result list and given query
       returns the result list with feedback
       '''
    def run_feedback(self, query):
        line_buffer = list()
        feedback = PseudoRelevanceFeedbackModel(self.result_id_list, 20, query, self.corpus_path)
        feedback.load_inverted_index(self.corpus_path+'/index/inverted_index.txt',
                                     self.corpus_path+'/index/doc_length.txt')
        feedback.calculate_top_freq_words(25, '../corpus_without_stopping')
        feedback.calculate_relevance_model()
        feedback_result = dict()
        for doc in self.doc_length.keys():
            divergence = feedback.calculate_kl_divergence_2(doc)
            feedback_result.update({doc: divergence})
        sorted_result = sorted(feedback_result.items(), key=lambda d: d[1], reverse=True)
        for i in range(0, 100):
            sorted_result[i] = str(sorted_result[i])
            doc_id = sorted_result[i][sorted_result[i].find('(') + 1:sorted_result[i].find(' ') - 1]
            score = sorted_result[i][sorted_result[i].find(' ') + 1:sorted_result[i].find(')')]
            line = 'Q0 ' + doc_id + ' ' + score
            line_buffer.append(line)
        return line_buffer