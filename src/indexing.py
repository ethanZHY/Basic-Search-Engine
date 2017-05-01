'''
Main indexing process:
initialing UniGramIndexer class inputs the corpus's path
write_inverted_index inputs the path where the index is going to be saved. For this project, save the index under the
directory of the related corpus
'''

from src.Indexer import UniGramIndexer


class Indexing:
    def main(self, path):        # path = ../corpus with stopping'
        indexer = UniGramIndexer(path)
        indexer.uni_gram_indexer()
        indexer.write_inverted_index(path + '/index')
