'''
Stemmer class acts to read the given stemmed text file and generates the stemmed version of each document and save them
seperately with the file name as same as original corpus' file name
'''

import re


class Stemmer:
    stemming_file_path = ''

    def __init__(self, output_path):        # output_path is the directory where the stemmed corpus to be saved
        # self.stemming_file_path = ''
        self.stemming_file_path = output_path

    '''
    method reads the stemmed file and save each stemmed version of document
    '''
    def generate_stemmed_corpus(self, stemmer_file):
        name = ''
        fr = open(stemmer_file)
        iterator = 0
        line = fr.readline()
        while line is not '':
            # seperate each document:
            if re.match('#\s\d', line):
                iterator += 1
                num = str(iterator)
                # generate document name in format : CACM-XXXX.txt
                length = len(num)
                if length == 1:
                    name = '000' + num
                if length == 2:
                    name = '00' + num
                if length == 3:
                    name = '0' + num
                if length == 4:
                    name = num
                file_name = 'CACM-' + name
                # write into txt file
                fw = open(self.stemming_file_path + '/' + file_name + '.txt', 'w', encoding='utf-8')
                line = fr.readline()
                while not re.match('#\s\d', line):
                    fw.write(line)
                    line = fr.readline()
                    if line is '':
                        break
                fw.close()