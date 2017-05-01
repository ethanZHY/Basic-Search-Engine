'''
main method to run the given test queries using TF-IDF model:
TfIdfRetrievalModel class reads 3 paths:
1. the corpus' inverted index file path
2. the corpus's doc_length file path
3. the corpus's path
'''

from src.TFIDFRetrievalModel import TfIdfRetrievalModel


class TFIDFSearching:
    def main(self,corpus_path,result_path,query_path,feedback):
        print('Initializing...')
        t = TfIdfRetrievalModel(corpus_path + '/index/inverted_index.txt',
                                corpus_path + '/index/doc_length.txt', corpus_path)
        t.calculate_doc_term_weight()   # build the document index structure to initialize the retrieval model
        '''
        read queries
        '''
        query_num = 0
        fr = open(query_path, 'r', encoding='utf-8')
        fw = open(result_path, 'w', encoding='utf-8')   # the path where to write the results
        # for each query, do the search and write the results
        for line in fr.readlines():
            query_num += 1
            query = str(line[line.find(' ')+1:len(line)-1])
            results = t.search(query, 100, feedback)
            for result in results:
                fw.write(str(query_num) + ' ' + result+'\n')

