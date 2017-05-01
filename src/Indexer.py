'''
unigram indexer, same with the indexer generated before
generates the uni-gram inverted lists and the hashMap storing each document's length
'''

import os


class UniGramIndexer:
    path = ''       # corpus' directory
    uni_gram_inverted_index = dict()  # store uni-gram inverted index
    uni_gram_set = set()  # store uni-gram tokens in the corpus
    doc_token_number = dict()  # store every docID's tokens number
    uni_gram_freq = dict()  # store uni-gram frequency
    doc_length = dict()     # store each document's length

    # constructor, reads the input directory which contains all documents
    def __init__(self, path):
        self.path = path

    def get_uni_gram_inverted_index(self):
        return self.uni_gram_inverted_index

    def get_doc_length(self):
        return self.doc_length

    def uni_gram_indexer(self):
        files = os.listdir(self.path)
        for file in files:
            if file.title().endswith('.Txt'):
                doc_length = 0
                fw = open(self.path + '/' + file, 'r', encoding='utf-8')
                doc_total_word_set = set()  # use a set to store the vocabulary of the document
                for line in fw.readlines():
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
                        doc_length += 1
                        doc_total_word_set.add(word)  # add word into vocabulary set
                        '''
                            If word has not been found, add it into the corpus vocabulary set, and add it into inverted index
                            key. If word has already been found in the corpus, check if the title is already in its value dict(),
                            if not, add title into its value map's key, if in, add title's value with 1
                        '''
                        if word not in self.uni_gram_set:
                            self.uni_gram_set.add(word)
                            # add to term frequency Map:
                            self.uni_gram_freq.update({word: 1})
                            # add to inverted index Map:
                            self.uni_gram_inverted_index.update({word: {file.title(): 1}})
                        else:
                            self.uni_gram_freq.update({word: self.uni_gram_freq.get(word) + 1})
                            inverted_list = self.uni_gram_inverted_index.get(word)
                            if file.title() in inverted_list.keys():
                                inverted_list.update({file.title(): inverted_list.get(file.title()) + 1})
                            else:
                                inverted_list.update({file.title(): 1})
                self.doc_token_number.update({file.title(): len(doc_total_word_set)})
                fw.close()
                self.doc_length.update({file.title(): doc_length})
                print('complete: '+file.title()+'\n')

        return

    def write_inverted_index(self, path):
        fw = open(path + '/inverted_index.txt', 'w', encoding='utf-8')
        for word in self.uni_gram_inverted_index.keys():
            fw.write(word + ' ')
            fw.write(str(self.uni_gram_inverted_index.get(word)) + '\n')
        fw.close()
        fw = open(path + '/doc_length.txt', 'w', encoding='utf-8')
        for title in self.doc_length:
            fw.write(title + ' ')
            fw.write(str(self.doc_length.get(title)))
            fw.write('\n')
        fw.close()
