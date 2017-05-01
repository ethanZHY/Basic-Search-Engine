'''
model runs the evaluation methods to evaluate the search engine: Evaluation methods includes:
1. Mean Average Precision
2. Mean Reciprocal Rank
3. Precision value at rank=5 and rank=20
4. Precision table and recall table for top 100 results for each query
'''

import os


class EvaluationModel:
    relevance_info_dict = dict()        # save the relevance information of each query
    query_result = dict()
    precision_dict = dict()
    recall_dict = dict()
    precision_at_5 = dict()
    precision_at_20 = dict()
    '''
    reads the relevance information text and save them into the HashMap. Map's key is the query number
    '''
    def __init__(self, text_path):
        self.relevance_info_dict = dict()  # save the relevance information of each query
        self.query_result = dict()
        self.precision_dict = dict()
        self.recall_dict = dict()
        self.precision_at_5 = dict()
        self.precision_at_20 = dict()
        print("initializing...")
        fr = open(text_path, 'r', encoding='utf-8')
        for line in fr.readlines():
            line = str(line)
            query_number = line[0:line.find(' ')]
            file_name = line[line.find('Q0 ')+3:line.rfind(' ')]
            # the text name in format: CACM-XXXX.txt
            word_part = file_name[0:file_name.find('-')+1]
            number_part = self.check_num(file_name[file_name.find('-')+1:])
            file_name = word_part + number_part
            if self.relevance_info_dict.get(query_number) is None:
                file_list = list()
                file_list.append(file_name)
                self.relevance_info_dict.update({query_number: file_list})
            else:
                file_list = self.relevance_info_dict.get(query_number)
                file_list.append(file_name)
                self.relevance_info_dict.update({query_number: file_list})
        fr.close()

    def check_num(self, num):
        if len(num) == 1:
            output = '000' + num
        elif len(num) == 2:
            output = '00' + num
        elif len(num) == 3:
            output = '0' + num
        else:
            output = num
        return output

    # set the query result path and run the evaluation
    def run(self, path, run):
            self.read_query_results(path + run)
            self.precision_at_k()
            for index_Q in range(1, 65):
                self.get_precision_table(str(index_Q))
                self.get_recall_table(str(index_Q))
                # self.evaluation_print(self.precision_dict, self.recall_dict, index_Q)
                self.evaluation_write(self.precision_dict, self.recall_dict, index_Q, run)

    def get_relevant_docs(self, query_number):
        return self.relevance_info_dict.get(query_number)

    def get_relevant_docs_number(self, query_number):
        return len(self.relevance_info_dict.get(query_number))

    # reads the search results of a given query number from the result text
    def read_query_results(self, run):
        fr = open(run, 'r', encoding='utf-8')
        for line in fr.readlines():
            query_number = line[0:line.find(' ')]
            file_name = line[line.find('Q0 ') + 4:line.find('.')].upper()
            if self.query_result.get(query_number) is None:
                file_list = list()
                file_list.append(file_name)
                self.query_result.update({query_number: file_list})
            else:
                file_list = self.query_result.get(query_number)
                file_list.append(file_name)
                self.query_result.update({query_number: file_list})
        fr.close()
    '''
    calculate the mean average precision of the queries
    '''
    def calculate_mean_average_precision(self):
        mean_sum = 0
        relevant_number = 0  # store the total number of queries that have relevance information
        for query_number in self.query_result.keys():
            curr_viewed = 0
            curr_relevant = 0
            precision_list = list()
            relevant_list = self.relevance_info_dict.get(query_number)
            result_list = self.query_result.get(query_number)
            if relevant_list is None:   # the query number has no relevance information, exclude
                continue
                # print("query" + query_number + "doesn't have relevance judgement")
            else:
                relevant_number += 1
                for i in range(0, len(result_list)):
                    result = result_list[i]
                    curr_viewed += 1
                    if result in relevant_list:
                        curr_relevant += 1
                        precision = curr_relevant / curr_viewed
                        precision_list.append(precision)
                # sum all precision values, calculate Average Precision
                summation = 0
                relevant_num = len(precision_list)
                for precision in precision_list:
                    summation += precision
                if relevant_num == 0:
                    average_precision = 0
                else:
                    average_precision = summation / relevant_num
                mean_sum += average_precision
        mean_average_precision = mean_sum / relevant_number
        return mean_average_precision

    '''
    calculate precision table for a query number
    '''
    def get_precision_table(self, query_number):
        self.precision_dict = dict()
        curr_relevant = 0
        result_list = self.query_result.get(query_number)
        relevant_list = self.relevance_info_dict.get(query_number)
        # print(relevant_list)
        if relevant_list is not None:
            for i in range(0, len(result_list)):
                rank = i + 1
                result = result_list[i]
                if result in relevant_list:
                    curr_relevant += 1
                precision = round(curr_relevant / rank, 3)
                self.precision_dict.update({rank: precision})
    '''
    calculate recall table for a query number
    '''
    def get_recall_table(self, query_number):
        self.recall_dict = dict()
        curr_relevant = 0
        result_list = self.query_result.get(query_number)
        relevant_list = self.relevance_info_dict.get(query_number)
        if relevant_list is not None:
            relevant_num = len(relevant_list)
            for i in range(0, len(result_list)):
                rank = i+1
                result = result_list[i]
                if result in relevant_list:
                    curr_relevant += 1
                recall = round(curr_relevant / relevant_num, 3)
                self.recall_dict.update({rank: recall})
    '''
    calculate Mean Reciprocal Rank for all queries:

    '''
    def calculate_mean_reciprocal_rank(self):
        mean_reciprocal = 0
        relevant_number = 0     # store the total number of queries that have relevance information
        for query_number in self.query_result.keys():
            relevant_list = self.relevance_info_dict.get(query_number)
            result_list = self.query_result.get(query_number)
            if relevant_list is None:       # the query number has no relevance information, exclude
                continue
                # print("query" + query_number + "doesn't have relevance judgement")
            else:
                relevant_number += 1
                for i in range(0, len(result_list)):
                    rank = i + 1
                    result = result_list[i]
                    if result in relevant_list:
                        reciprocal_rank = 1/rank        # get the reciprocal rank for query number results
                        mean_reciprocal += reciprocal_rank
                        break
        mean_reciprocal_rank = mean_reciprocal / relevant_number    # get MRR
        return mean_reciprocal_rank

    def precision_at_k(self):
        for query_number in self.query_result.keys():
            result_list = self.query_result.get(query_number)
            relevant_list = self.relevance_info_dict.get(query_number)
            if relevant_list is None:
                print("query" + query_number + "doesn't have relevance judgement")
            else:
                precision = 0
                for i in range(0, 5):
                    result = result_list[i]
                    if result in relevant_list:
                        precision += 1
                precision = precision / 5
                self.precision_at_5.update({query_number: precision})
                for i in range(0, 20):
                    result = result_list[i]
                    if result in relevant_list:
                        precision += 1
                precision = precision / 20
                self.precision_at_20.update({query_number: precision})
    '''
    def evaluation_print(self, precision_table, recall_table, index_Q):
        # for rank in precision_table.keys():
        #     print(str(rank) + ":p = " + str(precision_table.get(rank)) + " r = " + str(recall_table.get(rank)))
        print('MAP: '+ str(self.calculate_mean_average_precision()))
        print('MRR: '+ str(self.calculate_mean_reciprocal_rank()))
        print("precision @ 5:" + str(self.precision_at_5.get(str(index_Q))))
        print("precision @ 20:" + str(self.precision_at_20.get(str(index_Q))))
    '''
    '''
    write result into file
    '''
    # ../results/Evaluation/
    def evaluation_write(self, precision_table, recall_table, index_Q, run):
        newpath = '../result/Evaluation'
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        if index_Q == 1:
            fw = open(newpath + '/' + "Evaluation_" + run, 'w', encoding='utf-8')
            fw.write("Query:" + str(index_Q) + '\n')
        else:
            fw = open(newpath + '/' + "Evaluation_" + run, 'a', encoding='utf-8')
            fw.write("Query:" + str(index_Q) + '\n')
        for rank in precision_table.keys():
            fw.write(str(rank) + ":p = " + str(precision_table.get(rank)) + " r = " + str(recall_table.get(rank))+'\n')
        fw.write('MAP: ' + str(self.calculate_mean_average_precision())+'\n')
        fw.write('MRR: ' + str(self.calculate_mean_reciprocal_rank())+'\n')
        fw.write("precision @5: " + str(self.precision_at_5.get(str(index_Q)))+'\n')
        fw.write("precision @20: " + str(self.precision_at_20.get(str(index_Q)))+'\n\n')
        fw.close()




