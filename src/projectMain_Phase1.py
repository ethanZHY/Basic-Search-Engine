from src.tokenizing import Tokenizing
from src.indexing import Indexing
from src.TFIDFSearching import TFIDFSearching
from src.BM25Searching import BM25Searching
from src.stemming import Stemming


print('CS6200-project')
print('Phase1:Indexing and Retrieval: ')
print('Task1---baseline search:')
print('generate corpus:')


# without_stopping_path = input('input the directory to save corpus(../corpus_without_stopping):\n')
without_stopping_path = "../corpus_without_stopping"
print('generating corpus...')
without_stopping = Tokenizing()
without_stopping.main(without_stopping_path, remove_stop_word=False)
print('generating index..')
indexer = Indexing()
indexer.main(without_stopping_path)

# Task1:
without_stopping_path = '../corpus_without_stopping'
print('Now run the queries:')
# query_path = input('input query path:(../cacm_query_new.txt):\n')
query_path = '../cacm_query_new.txt'
print('TF-IDF Retrieval Model:')
# tf_idf_result_path = input('input result path: (../result/baseline/tf-idf_baseline.txt)\n')
tf_idf_result_path = "../result/baseline/tf-idf_baseline.txt"
tf_idf_baseline_search = TFIDFSearching()
tf_idf_baseline_search.main(corpus_path=without_stopping_path,
                            result_path=tf_idf_result_path, query_path=query_path, feedback=False)
print('TF-IDF search success!')
print('BM25 Retrieval Model:')
bm25_result_path = "../result/baseline/BM25_baseline.txt"
bm25_baseline_search = BM25Searching()
bm25_baseline_search.main(corpus_path=without_stopping_path,
                          result_path=bm25_result_path, query_path=query_path,
                          k_1=3.0, k_2=100, b=0.78, feedback=False)
print('BM25 search success!')
# Task2:
print('Task2--Pseudo Relevance Feedback search:')
print('TF-IDF Retrieval Model:')
tf_idf_result_path = "../result/pseudo_relevance_feedback/tf-idf_PRF.txt"
tf_idf_baseline_search = TFIDFSearching()
tf_idf_baseline_search.main(corpus_path=without_stopping_path,
                            result_path=tf_idf_result_path, query_path=query_path, feedback=True)
print('TF-IDF pseudo relevance feedback search success!')

print('BM25 Retrieval Model:')
bm25_result_path = "../result/pseudo_relevance_feedback/BM25_PRF.txt"
bm25_baseline_search = BM25Searching()
bm25_baseline_search.main(corpus_path=without_stopping_path,
                          result_path=bm25_result_path, query_path=query_path,
                          k_1=3.0, k_2=100, b=0.78, feedback=True)
print('BM25 pseudo relevance feedback search success!')

# Task3:
print("Task3:\n ")
print('Stopping with no stemming:')
with_stopping_path = "../corpus_with_stopping"
print('generating corpus...')
removal_stopping = Tokenizing()
removal_stopping.main(with_stopping_path, remove_stop_word=True)
print('generating index..')
indexer = Indexing()
indexer.main(with_stopping_path)
print('perform tf-idf search:')
tf_idf_result_path = "../result/stopping/tf-idf_stopping.txt"
query_path = "../cacm_query_new.txt"
tf_idf_baseline_search = TFIDFSearching()
tf_idf_baseline_search.main(corpus_path=with_stopping_path,
                            result_path=tf_idf_result_path, query_path=query_path, feedback=False)
print('TF-IDF pseudo relevance feedback search success!')
print('BM25 Retrieval Model:')
bm25_result_path = "../result/stopping/BM25_stopping.txt"
bm25_baseline_search = BM25Searching()
bm25_baseline_search.main(corpus_path=with_stopping_path,
                          result_path=bm25_result_path, query_path=query_path,
                          k_1=3.0, k_2=100, b=0.78, feedback=False)
print('BM25 pseudo relevance feedback search success!')

print('Stemmed version of corpus:')
stemmer = Stemming()
stem_path = "../stemmed_corpus"
stemmer.main(stem_path)
indexer = Indexing()
indexer.main(stem_path)

print('perform tf-idf search:')
tf_idf_result_path = "../result/stemming/tf-idf_stemming.txt"
query_path = "../cacm_stem_query.txt"
tf_idf_baseline_search = TFIDFSearching()
tf_idf_baseline_search.main(corpus_path=stem_path,
                            result_path=tf_idf_result_path, query_path=query_path, feedback=False)

print('perform BM25 search:')
BM25_result_path = "../result/stemming/BM25_stemming.txt"
query_path = "../cacm_stem_query.txt"
bm25_baseline_search = BM25Searching()
bm25_baseline_search.main(corpus_path=stem_path,
                            result_path=BM25_result_path, query_path=query_path,
                          k_1=3.0, k_2=100, b=0.78,feedback=False)

