'''
    Tokenizer acts to tokenize the original cacm corpus into tokenized corpus, including removing stopwords, removing
    punctuation and convert html format into plain text format.
'''

import os
import re


class Tokenizer:
    tokenized_file_path = ''
    stop_words = set()

    # create the directory where the tokenized corpus to be saved
    def create_directory(self, path):       # path: where the tokenized corpus to be generated
            is_exists = os.path.exists(path)
            if is_exists:
                print('directory already exists!')
            else:
                os.makedirs(path)
            self.tokenized_file_path = path

    # read stopwords from stopword text file, add all words into global variable stop_words
    def generate_stop_words(self, txt):
        stop_words_file = open(txt, 'r', encoding='utf-8')
        for line in stop_words_file.readlines():
            stop_word = line.replace('\n', '')
            self.stop_words.add(stop_word)

    '''
    main tokenization process: read html file from original corpus, convert it to txt file, and save to specified path
    path: directory of original corpus
    remove_stopword: flag to control whether or not to remove stopwords. True: yes; False: no
    '''
    def tokenization(self, path, remove_stopword):
        files = os.listdir(path)
        for file in files:
            words_list = list()
            self.convert_html_to_wordlist(file, path, words_list)
            if remove_stopword is True:
                words_list = self.remove_stop_words(words_list)
            file_name = file.replace('.html', '.txt')
            file_name = self.tokenized_file_path + '/' + file_name
            self.write_word_list_to_txt(words_list, file_name)

    # write the words list generated from convert_html_to_wordlist method into txt file
    def write_word_list_to_txt(self, words_list, filename):
        fw = open(filename, 'w', encoding='utf-8')
        for word in words_list:
            word = word.replace('\t', ' ')
            fw.write(word + ' ')
        fw.close()

    # remove stopwords from the wordlist generated from convert_html_to_wordlist method
    def remove_stop_words(self, words_list):
        stop_words_removed = list()
        for word in words_list:
            if word not in self.stop_words:
                stop_words_removed.append(word)
        return stop_words_removed

    '''
    method reads html file from original cacm corpus, get all words from the html file, and return the words list
    file: the html file
    path: directory of original html corpus
    '''
    def convert_html_to_wordlist(self, file, path, word_list):
        line_buffer = list()
        if not os.path.isdir(file):
            file_reader = open(path + '/' + file, 'r', encoding='utf-8')
            for line in file_reader.readlines():
                line = line.casefold()          # case-folding
                # remove the number table part at the bottom of the html file
                if re.match('ca\d\d\d\d\d\d\sjb', line):
                    line_buffer.append(str(line))
                    break
                line_buffer.append(str(line))
            find_title = 0
            i = 0
            while i < len(line_buffer):
                line = str(line_buffer[i])
                # remove <html> and <pre> tags
                if line.find('<html>') != -1 or line.find('<pre>') != -1 or line.find('</pre>') != -1 or line.find(
                        '</html>') != -1:
                    i += 1
                    continue
                if line == '\n':
                    find_title += 1
                    word_list.append(line)
                    i += 1
                    continue
                if line.find('.\n') == -1:
                    line = self.remove_punctuation(line)  # remove punctuation
                    line = line.replace('\n', ' ')
                    words_list = line.split(' ')
                    for word in words_list:
                        if word != '':
                            word_list.append(word)
                else:
                    process_line = self.remove_punctuation(line)  # remove punctuation
                    process_line = process_line.replace('\n', ' ')
                    words_list = process_line.split(' ')
                    for word in words_list:
                        if word != '':
                            word_list.append(word)
                    word_list.append('\n')
                i += 1

    '''
    remove punctuation in following way:
    1. replace [,],{,},“,” with space
    2. replace all ",',(),;,:,+,*,/,=,`, en dash and em dash  with space
    3. replace \xa0, which is nbsp, with space
    4. replace all ',' '.' with space that are following behind word character and followed by non-word character. Like
        , . in the end of sentence and text...text
    5. replace all ',' '.' that acts as apostrophe， while keep , . within digits
    6. replace - that are not hyphen in form 'text-text',
    7. replace nonXML parts in the text(^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\u10000-\u10FFFF) for later snippet
    generation use
    '''
    def remove_punctuation(self, text):
        processed_text = str(text).replace('[', ' ').replace(']', ' ').replace('{', ' ').replace('}', ' '). \
            replace("'", ' ')
        processed_text = re.sub('(?=\s)[-](?=\s)', ' ', processed_text)  # remove things like -text
        processed_text = re.sub('["();?“”+*/=`><ˈ‘～’~\\\\–—]', ' ', processed_text)
        processed_text = re.sub('(?!\d)[:]](?!\d)', ' ', processed_text)
        processed_text = re.sub('[\ufeff\u200a\u2009\u2003\u2002\u200e\u2060\u200d\u200c\u200b\u202f\x80\x93\xa0]', ' ',
                                processed_text)
        processed_text = re.sub('(?=\w)[,.](?=\W)', ' ', processed_text)  # remove those ',', '.' followed by space
        processed_text = re.sub('(?=\W)[.,](?=\D)', ' ', processed_text)
        processed_text = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\u10000-\u10FFFF]+', '', processed_text)
        return processed_text
