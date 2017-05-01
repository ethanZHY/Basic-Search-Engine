'''
Model generates snippet for a document given a query following:
1. convert each documents into sentences.
2. for each sentence, rank them by Luhn's significant terms concept and evaluation formula.
3. for the ranked sentences, calculate the snippet generation score use 1/(log2(rank)+1) * query terms frequency/sentenc
e length:  Rank is the rank of sentence's significance, query terms frequency is the time query words appear in sentence
sentence length used for normalization.
4. rank the top 3 sentences by snippet generation score to be the snippet
'''

import re
import math


class SnippetGenerator:
    # remove punctuation from a text in methods as before
    def remove_punctuation(self, text):
        processed_text = str(text).replace('[', ' ').replace(']', ' ').replace('{', ' ').replace('}', ' '). \
            replace("'", ' ')
        processed_text = re.sub('(?=\s)[-](?=\s)', ' ', processed_text)  # remove things like -text
        processed_text = re.sub('["();?“”+*/=`><ˈ‘～’~\\\\–—-]', ' ', processed_text)
        processed_text = re.sub('(?!\d)[:]](?!\d)', ' ', processed_text)
        processed_text = re.sub('[\ufeff\u200a\u2009\u2003\u2002\u200e\u2060\u200d\u200c\u200b\u202f\x80\x93\xa0]', ' ',
                                processed_text)
        processed_text = re.sub('(?=\w)[,.](?=\W)', ' ', processed_text)  # remove those ',', '.' followed by space
        processed_text = re.sub('(?=\W)[.,](?=\D)', ' ', processed_text)
        processed_text = re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\u10000-\u10FFFF]+', '', processed_text)
        return processed_text

    # process html file into sentences list, return sentences list
    def doc_process(self, doc):
        word_list = list()
        fr = open(doc,'r',encoding='utf-8')
        line_buffer = list()
        for line in fr.readlines():
            if re.match('CA\d\d\d\d\d\d\sJB',line):
                line_buffer.append(line)
                break
            line_buffer.append(line)
        i = 0
        while i < len(line_buffer):
            line = str(line_buffer[i])
            if line.find('<html>') != -1 or line.find('<pre>') != -1 or line.find('</pre>') != -1 or line.find(
                    '</html>') != -1:
                i += 1
                continue
            if line == '\n':
                i += 1
                word_list.append(line)
                continue
            if line.find('.\n') == -1:
                line = line.replace('\n', ' ')
                words_list = line.split(' ')
                for word in words_list:
                    if word != '':
                        word_list.append(word)
            else:
                words_list = line.split(' ')
                for word in words_list:
                    if word != '':
                        word_list.append(word)
                word_list.append('\n')
            i += 1
        sentence_list = list()
        sentence = ''
        iterator = 0
        while iterator < len(word_list):
            while word_list[iterator] == '\n':
                iterator += 1
                if iterator == len(word_list):
                    break
            if iterator == len(word_list):
                break
            while word_list[iterator] != '\n':
                if word_list[iterator].find('.\n') != -1:
                    word_list[iterator] = word_list[iterator][0:len(word_list[iterator])-1]
                sentence += word_list[iterator] + ' '
                if word_list[iterator][len(word_list[iterator])-1] == '.':
                    iterator += 1
                    break
                iterator += 1
                if iterator == len(word_list):
                    break
            sentence = sentence[0:len(sentence)-1]
            sentence_list.append(sentence)
            sentence = ''
        return sentence_list

    '''
    find significant term in a document using significant term's concept by Luhn
    '''

    def find_significant_term(self, sentence_list):
        significant_term_set = set()
        word_freq = dict()
        s_d = len(sentence_list)
        if s_d < 25:
            judgement = 7 - 0.1 * (25-s_d)
        elif 25 <= s_d <= 40:
            judgement = 7
        else:
            judgement = 7 + 0.1 * (s_d - 40)
        for sentence in sentence_list:
            sentence = self.remove_punctuation(sentence).casefold()
            words = sentence.split(' ')
            # get each word's frequency
            for word in words:
                if word is '':
                    continue
                if word in word_freq.keys():
                    word_freq.update({word: word_freq.get(word)+1})
                else:
                    word_freq.update({word: 1})
        # find significant term
        for word in word_freq.keys():
            word_frequency = word_freq.get(word)
            if word_frequency >= judgement:
                significant_term_set.add(word)
        return significant_term_set

    '''
    rank the sentences by significant term's appearance
    '''
    def rank_significant_sentence(self, significant_term_set, sentence_list):
        sentence_score_list = dict()
        num = 0  # label the sentence
        for sentence in sentence_list:
            sentence = self.remove_punctuation(sentence).casefold()
            words = sentence.split(' ')
            words_list = list()
            for word in words:
                if word is '':
                    continue
                else:
                    words_list.append(word)
            '''
            find bracket of significant terms in the sentence
            '''
            pos = 0
            neg = len(words_list)-1
            while words_list[pos] not in significant_term_set:
                pos += 1
                if pos == len(words_list):
                    break

            while words_list[neg] not in significant_term_set:
                neg -= 1
                if neg == -1:
                    break
            if pos == len(words_list):
                significant_length = 0
            else:
                significant_length = neg - pos + 1
            #  calculate score with bracket's length^2 / sentence length
            score = math.pow(significant_length,2) / len(words_list)
            sentence_score_list.update({num: score})
            num += 1
        # sort the sentence by significant score
        sorted_sentence_label = sorted(sentence_score_list.items(), key=lambda d: d[1], reverse=True)
        sorted_sentence_labels = list()
        for result in sorted_sentence_label:
            result = str(result)
            num = result[result.find('(')+1:result.find(',')]
            num = int(num)
            sorted_sentence_labels.append(num)

        return sorted_sentence_labels

    '''
    represent the sentence by the order they appears in document
    generate the snippet. for the ranked sentences list by siginicant score,
    calculate the sentences again with relation with query as well as the significance in document
    use evaluation formula: score = 1/(log2(rank)+1)* frequency of query terms in sentence/sentence length
    then score the top 3 score sentences to be the snippet
    '''
    def snippet_generation(self, query_words, sentence_label, sentence_list):
        snippet_dict = dict()
        rank = 0
        for label in sentence_label:
            rank += 1
            sentence = sentence_list[label]
            sentence = self.remove_punctuation(sentence).casefold()
            sentence_words = sentence.split(' ')
            sentence_length = len(sentence_words)
            query_word_freq = 0
            for word in sentence_words:
                if word in query_words:
                    query_word_freq += 1
            score = 1/(math.log2(rank)+1) * query_word_freq / sentence_length
            snippet_dict.update({label: score})
        sorted_score = sorted(snippet_dict.items(), key=lambda d: d[1], reverse=True)
        sorted_labels = list()
        for score in sorted_score:
            score = str(score)
            label = score[score.find('(')+1:score.find(',')]
            label = int(label)
            sorted_labels.append(label)
        return sorted_labels
