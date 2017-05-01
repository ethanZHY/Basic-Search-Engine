'''
Model runs pseudo relevance feedback
    assume top n results to be relevant
    one query
Model works as:
1.reads the relevant corpus from initial search result
2. for the relevant corpus, calculate the top some number of frequent words
3. Use these words and the query to build a relevance model
4. use the relevance model to compute each document's kl-divergence score and re-rank the documents
'''
import math


class PseudoRelevanceFeedbackModel:
    sample_doc_list = list()        # relevant corpus
    corpus_path = ''
    query_word = dict()
    inverted_index = dict()
    doc_length = dict()
    top_frequent_word_set = set()
    query_length = 0
    corpus_size = 0
    term_frequency = dict()
    relevance_prob = dict()
    relevance_sum = 0

    '''
    constructor initialize all global variables and set the corpus's path
    '''
    def __init__(self, results, num, query, corpus_path):
        self.sample_doc_list = list()
        self.corpus_path = ''
        self.doc_length = dict()
        self.top_frequent_word_set = set()
        self.query_length = 0
        self.corpus_size = 0
        self.term_frequency = dict()
        self.relevance_prob = dict()
        self.relevance_sum = 0
        self.query_word = dict()
        self.inverted_index = dict()
        self.corpus_path = corpus_path
        # add result docID into relevant corpus document list
        for i in range(0, num):
            self.sample_doc_list.append(results[i])
        words_list = query.split(' ')
        for word in words_list:
            self.query_length += 1
            if word in self.query_word:
                self.query_word.update({word: self.query_word.get(word)+1})
            else:
                self.query_word.update({word: 1})

    # calculate the relevance model of relevant corpus
    def calculate_relevance_model(self):
        self.get_corpus_term_frequency()
        self.calculate_corpus_size()
        self.calculate_relevance_model_sum()
        self.calculate_top_freq_word_relevance_prob()

    def load_inverted_index(self, index_path, doc_length_path):
        fw1 = open(doc_length_path, 'r', encoding='utf-8')
        for line in fw1.readlines():
            doc_id = line[:line.find(' ')]
            freq = float(line[line.find(' ') + 1: line.rfind('\n')])
            self.doc_length.update({doc_id: freq})
        fw1.close()
        # read inverted list:
        fw1 = open(index_path, 'r', encoding='utf-8')
        for line in fw1.readlines():
            term = line[:line.find(' ')]
            line = line[line.find(' ') + 1:]
            index = dict()
            lists = line.split(', ')
            for l in lists:
                if l.find('\n') != -1:
                    l = l[:l.find('\n')]
                doc_id = l[l.find("'") + 1:l.find(':') - 1]
                if l.find('}') != -1:
                    freq = l[l.find(':') + 2:l.find('}')]
                else:
                    freq = l[l.find(':') + 2:]
                index.update({doc_id: float(freq)})
                self.inverted_index.update({term: index})

    # P(w,q1,q2,...,qn) = for all document in sample documents, sum p(w|D)*P(qi|D)
    # calculate p(w|D) and p(w|Q) use dirichlet smoothing
    def calculate_joint_probability(self, term):
        query_words = self.query_word.keys()
        summation = 0
        for doc in self.sample_doc_list:
            query_part = 1
            for query_word in query_words:
                prob = self.dirichlet_smoothing(query_word, doc, 50)
                if prob == 0:
                    query_part *= 1     # if the probability is 0, multiply with 1 to avoid become 0
                else:
                    query_part *= prob
            term_part = self.dirichlet_smoothing(term, doc, 50)
            summation += term_part*query_part
        return summation

    # calculate each term in the top frequently appearing word set's p(w,q1,q2,...,qn), store in a HashMap
    def calculate_top_freq_word_relevance_prob(self):
        for term in self.top_frequent_word_set:
            prob_list = list()
            prob_list.append(self.calculate_joint_probability(term))
            if self.query_word.get(term) is None:
                query_probability = 0
            else:
                query_probability = self.query_word.get(term)/self.query_length
            prob_list.append(query_probability)
            self.relevance_prob.update({term: prob_list})

    # calculate sumP(w,q1,q2...qn)
    def calculate_relevance_model_sum(self):
        summation = 0
        for v in self.top_frequent_word_set:
            summation += self.calculate_joint_probability(v)
        self.relevance_sum = summation

    '''
    calculate KL-divergence use sum by w (p(w|R)*log(p(w|D)))
    p(w|R) = 0.5*p(w|R) + 0.5*p(w|Q))
    calculate use: score = 0.5*(1/sumP(w,q1,...,qn)) * sum(P(w,q1,...,qn)*log(p(w|D)) + 0.5*sum(P(w|Q)*log(p(w|D)))
    '''
    def calculate_kl_divergence_2(self, doc):
        first_part = 0
        second_part = 0
        for term in self.top_frequent_word_set:
            # logP(w|D), add 1 to let log part >0, easy to examine
            log_part = math.log10(self.dirichlet_smoothing(term, doc, 100) + 1)
            relevance_prob = self.relevance_prob.get(term)[0]
            query_prob = self.relevance_prob.get(term)[1]
            first_part += relevance_prob * log_part
            second_part += query_prob * log_part
        if self.relevance_sum == 0:
            divergence = 0
        else:
            divergence = 0.5/self.relevance_sum * first_part + 0.5*second_part
        return divergence

    # get the top num frequent words from relevant corpus
    def calculate_top_freq_words(self, num, corpus_path):       # corpus path is the corpus with stopwords removed
        term_freq_dict = dict()
        for doc_id in self.sample_doc_list:     # get document from relevant corpus
            doc_name = doc_id[0:doc_id.find('.Txt')]
            doc_name = doc_name.upper()
            doc_id = doc_name + '.Txt'
            # read the file from the corpus that has removed stop words
            fr = open(corpus_path + '/' + doc_id, 'r', encoding='utf-8')
            for line in fr.readlines():
                words_list = list()  # store each line's all word in a list
                for word in line.split(' '):
                    words_list.append(word)
                n = len(words_list)
                # delete the '\n' in every line's last word
                last = words_list.pop(n - 1)
                last = last[:len(last) - 1]
                words_list.insert(n - 1, last)
                for word in words_list:
                    if word is '':  # delete all empty in the word list
                        continue
                    if word not in term_freq_dict.keys():
                        term_freq_dict.update({word: 1})
                    else:
                        term_freq_dict.update({word: term_freq_dict.get(word)+1})
        sorted_terms = sorted(term_freq_dict.items(), key=lambda d: d[1], reverse=True)
        for i in range(0, num):
            sorted_terms[i] = str(sorted_terms[i])
            word = sorted_terms[i][sorted_terms[i].find("'")+1:sorted_terms[i].find("',")]
            self.top_frequent_word_set.add(word)

    # calculate P(w|D) with dirichlet smoothing
    def dirichlet_smoothing(self, word, doc, miu):
        probability = 0
        if self.inverted_index.get(word) is None:
            return probability
        else:
            if self.inverted_index.get(word).get(doc) is None:
                term_freq_doc = 0
            else:
                term_freq_doc = float(self.inverted_index.get(word).get(doc))
            doc_length = self.doc_length.get(doc)
            term_freq_corpus = 0
            if self.term_frequency.get(word) is not None:
                term_freq_corpus = self.term_frequency.get(word)
            probability = (term_freq_doc + miu*(term_freq_corpus/self.corpus_size)) / (doc_length+miu)
            return probability

    # calculate the corpus' s size use in dirichlet smoothing
    def calculate_corpus_size(self):
        for doc in self.doc_length.keys():
            self.corpus_size += float(self.doc_length.get(doc))

    # get each term's frequency in the corpus use in dirichlet smoothing
    def get_corpus_term_frequency(self):
        for term in self.inverted_index.keys():
            term_freq_corpus = 0
            inverted_list = self.inverted_index.get(term)
            for doc in inverted_list.keys():
                term_freq_corpus += int(inverted_list.get(doc))
            self.term_frequency.update({term: term_freq_corpus})
