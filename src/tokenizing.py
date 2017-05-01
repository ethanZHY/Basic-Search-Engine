'''
    main tokenizing process:
    input create_directory the path where the tokenized corpus to be saved
    input generate_stop_words the path where the stopwords file exists
    input tokenization the path where the original corpus is located and whether or not the tokenization removes
    stopword
'''

from src.Tokenizer import Tokenizer
class Tokenizing:

    def main(self, path, remove_stop_word):
        t = Tokenizer()
        t.create_directory(path)
        t.generate_stop_words('../common_words.txt')
        t.tokenization('../cacm', remove_stopword=remove_stop_word)
