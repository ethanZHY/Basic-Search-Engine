'''
This is a model to calculate documents score for a query based on tf-idf calculation using vector space model,
And do the search function, rank the top documents by vector space model score given a query
'''

import math
from src.PseudoRelevenceFeedbackModel import *
from src.Tokenizer import *


class TfIdfRetrievalModel:
    uni_gram_inverted_list = dict()
    doc_length = dict()
    doc_term_weight_dict = dict()
    doc_index = dict()
    corpus_path = ''
    '''
    initialze the Class with the path of the inverted list and the doc_length file generated from indexer
    inverted_lists and doc_length HashMap's keys are documentID in format: 'CACM-XXXX.Txt'
    '''
    def __init__(self, inverted_list_path, doc_length_path, corpus_path):
        self.uni_gram_inverted_list = dict()
        self.doc_length = dict()
        self.doc_term_weight_dict = dict()
        self.doc_index = dict()
        self.corpus_path = ''
        # read document length into HashMap:
        self.corpus_path = corpus_path
        fw1 = open(doc_length_path, 'r', encoding='utf-8')
        for line in fw1.readlines():
            doc_id = line[:line.find(' ')]
            freq = line[line.find(' ')+1: line.rfind('\n')]
            self.doc_length.update({doc_id: float(freq)})
        fw1.close()
        # read inverted list into HashMap:
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
                index.update({doc_id: float(freq)})
                self.uni_gram_inverted_list.update({term: index})

    # get the frequency of a specified term in a document fik
    def get_tf(self, term, doc_title):
        freq = 0
        term_inverted_list = self.uni_gram_inverted_list.get(term)
        if term_inverted_list is None:
            return freq
        if term_inverted_list.get(doc_title) is None:
            return freq
        else:
            freq = term_inverted_list.get(doc_title)
            return freq

    # get the inverted document frequency in format log(N/nk)
    def get_idf(self, term):
        total_doc = len(self.uni_gram_inverted_list.keys()) + 1
        # idf = 1     # avoid /0
        term_inverted_list = self.uni_gram_inverted_list.get(term)
        if term_inverted_list is None:              # term does not appear in corpus,set idf to be 0
            return 0
        else:
            idf = len(term_inverted_list.keys())
            return math.log10(total_doc / idf)

    '''
    calculate each term's weight in the query:
    dik = (log(fik+1))*log(N/nk)/sqrt(sum(log(fik+1)*log(N/nk)))
    fik = frequency of term in query
    nk = number of appear documents containing term in the corpus
    sqrt(sum(log(fik+1)*log(N/nk))) is normalization part
    '''
    def calculate_query_weight2(self, query):
        query_weight = dict()
        query_dict = dict()         # store term's frequency in query
        N = len(self.doc_length.keys())
        query_words = query.split(' ')
        summation = 0       # used for normalization
        for word in query_words:
            if word not in query_dict:
                query_dict.update({word: 1})
            else:
                query_dict.update({word: query_dict.get(word) + 1})
        for word in query_dict.keys():
            query_freq = query_dict.get(word)       # get term's frequency
            if self.uni_gram_inverted_list.get(word) is None:       # if the term does not appear in documents
                query_w = 0     # set query weight to be 0
            else:
                query_w = (math.log10(query_freq)+1) * self.get_idf(word)   # (log(fik+1))*log(N/nk)
                summation += math.pow(query_w, 2)
            query_weight.update({word: query_w})
        normalization = math.sqrt(summation)
        # if normalization!=0, do the normalization; if =0, means query weight is 0, do not need to normalize
        if normalization != 0:
            for word in query_weight.keys():
                query_weight.update({word: query_weight.get(word)/normalization})
        return query_weight

    # build doc index builds a document index where index's structure is {document:{term:frequency}}
    def build_doc_index(self):
        for doc in self.doc_length.keys():
            self.doc_index.update({doc: dict()})
        for term in self.uni_gram_inverted_list.keys():
            for doc in self.uni_gram_inverted_list.get(term).keys():
                self.doc_index.get(doc).update({term: self.get_tf(term, doc)})

    '''
        calculate each term's weight in the document:
        dik = (log(fik+1))*log(N/nk)/sqrt(sum(log(fik+1)*log(N/nk)))
        fik = frequency of term in document
        nk = number of appear documents containing term in the corpus
        sqrt(sum(log(fik+1)*log(N/nk))) is normalization part
        '''
    def calculate_doc_term_weight(self):
        self.build_doc_index()          # build document index
        for doc in self.doc_length.keys():
            document_term_weight_dict = dict()  # hashMap to store the document's term and their weights
            normalization = 0
            # calculate the normalization value
            for term in self.doc_index.get(doc).keys():
                if doc in self.uni_gram_inverted_list.get(term).keys():
                    term_freq = self.doc_index.get(doc).get(term)
                    term_idf = self.get_idf(term)
                    document_term_weight_dict.update({term: 0})
                    normalization += (math.log10(term_freq)+1)*term_idf
            normalization = math.sqrt(normalization)
            # calculate each term's weight in the document
            for term in document_term_weight_dict.keys():
                term_freq = self.get_tf(term, doc)
                term_idf = self.get_idf(term)
                weight = ((math.log10(term_freq)+1)*term_idf) / normalization
                document_term_weight_dict.update({term: weight})
            self.doc_term_weight_dict.update({doc: document_term_weight_dict})

    '''
    calculate the vector space model score:
    cos(D,Q) = sum(dij*qj)/sqrt(sum(dij)*sum(qj))
    '''
    def calculate_score(self, doc, query):
        query_weight_dict = self.calculate_query_weight2(query)
        document_term_weight_dict = self.doc_term_weight_dict.get(doc)
        score = 0
        doc_term_sum = 0
        query_term_sum = 0
        for term in document_term_weight_dict.keys():
            if term in query_weight_dict.keys():
                q = query_weight_dict.get(term)
            else:
                q = 0

            d = document_term_weight_dict.get(term)
            score += d*q
            doc_term_sum += math.pow(d, 2)
            query_term_sum += math.pow(q, 2)
            if query_term_sum == 0:         # avoid division by zero
                query_term_sum = 1
        score /= math.sqrt(doc_term_sum*query_term_sum)
        return score

    '''
    search result based on query, num variable is the number of results shown
    run_feedback is the flag to control whether or not to run pseudo relevance feedback
    method returns a list of results
    '''
    def search(self, query, num, run_feedback):
        result_id_list = list()
        score_dict = dict()
        for doc in self.doc_length.keys():
            score = self.calculate_score(doc, query)
            score_dict.update({doc: score})
        sorted_result = sorted(score_dict.items(), key=lambda d: d[1], reverse=True)
        line_buffer = list()
        for i in range(0, num):
            sorted_result[i] = str(sorted_result[i])
            doc_id = sorted_result[i][sorted_result[i].find('(') + 1:sorted_result[i].find(' ') - 1]
            score = sorted_result[i][sorted_result[i].find(' ') + 1:sorted_result[i].find(')')]
            line = 'Q0 ' + doc_id + ' ' + score
            result_id_list.append(doc_id[doc_id.find("'") + 1:doc_id.rfind("'")])
            line_buffer.append(line)
        query_tokenize = Tokenizer()
        query = query_tokenize.remove_punctuation(query)
        # True to run pseudo relevance feedback
        if run_feedback is True:
            line_buffer = self.run_feedback(query, result_id_list)
        # self.save_result(query, line_buffer)
        return line_buffer
    '''
    method to run pseudo relevance feedback on given result list and given query
    returns the result list with feedback
    '''
    def run_feedback(self, query, result_id_list):
        line_buffer = list()
        # initialze a PseudoRelevanceFeedbackModel object
        feedback = PseudoRelevanceFeedbackModel(result_id_list, 20, query, self.corpus_path)
        feedback.load_inverted_index(self.corpus_path + '/index/inverted_index.txt',
                                     self.corpus_path + '/index/doc_length.txt')
        # set top 25 frequent word to examine to increase effeciency
        feedback.calculate_top_freq_words(25, '../corpus_without_stopping')
        feedback.calculate_relevance_model()    # calculate relevance model
        feedback_result = dict()
        # calculate KL-divergence for documents and resort them by KL-divergence score
        for doc in self.doc_length.keys():
            divergence = feedback.calculate_kl_divergence_2(doc)
            feedback_result.update({doc: divergence})
        sorted_result = sorted(feedback_result.items(), key=lambda d: d[1], reverse=True)
        for i in range(0, 100):
            sorted_result[i] = str(sorted_result[i])
            doc_id = sorted_result[i][sorted_result[i].find('(') + 1:sorted_result[i].find(' ') - 1]
            score = sorted_result[i][sorted_result[i].find(' ') + 1:sorted_result[i].find(')')]
            # print(score)
            line = 'Q0 ' + doc_id + ' ' + score
            line_buffer.append(line)
        return line_buffer
