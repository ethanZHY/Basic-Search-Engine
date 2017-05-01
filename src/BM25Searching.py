'''
Main method to run the given test queries using BM25 Retrieval model:
TfIdfRetrievalModel class reads 3 paths:
1. the corpus' inverted index file path
2. the corpus's doc_length file path
3. the corpus's path
'''
from src.BM25RetrievalModel import BM25RetrievalModel


class BM25Searching:

    def main(self,corpus_path, result_path, query_path, k_1, k_2, b, feedback):
        print('Initializing...')
        model = BM25RetrievalModel(corpus_path + '/index/inverted_index.txt',
                                        corpus_path + '/index/doc_length.txt', corpus_path)
        model.k_1 = k_1
        model.k_2 = k_2
        model.b = b
        '''
        read queries
        '''
        query_num = 0
        fr = open(query_path, 'r', encoding='utf-8')
        fw = open(result_path, 'w', encoding='utf-8')    # the path where to write the results
        # for each query, do the search and write the results
        for line in fr.readlines():
            query_num += 1
            query = str(line[line.find(' ') + 1:len(line) - 1])
            print(query)
            results = model.search(query, 100, feedback)
            for result in results:
                fw.write(str(query_num) + ' ' + result+'\n')
            print(query_num)
