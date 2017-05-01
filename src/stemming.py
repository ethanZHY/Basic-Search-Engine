'''
Stemming main process:
initialize the class with the directory where the corpus to be saved
generate_stemmed_corpus takes the input variable of the path where the stem file is located
'''

from src.Stemmer import Stemmer


class Stemming:
    def main(self, path):
        stem = Stemmer(path)
        stem.generate_stemmed_corpus('../cacm_stem.txt')
