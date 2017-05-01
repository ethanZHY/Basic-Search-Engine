
class EvaluationModel:
    relevance_info_dict = dict()
    query_result = dict()

    def __init__(self, text_path):
        fr = open(text_path, 'r', encoding= 'utf-8')
        for line in fr.readlines():
            line = str(line)
            query_number = line[0:line.find(' ')]
            file_name = line[line.find('Q0 ')+3:line.rfind(' ')]
            if self.relevance_info_dict.get(query_number) is None:
                file_list = list()
                file_list.append(file_name)
                self.relevance_info_dict.update({query_number: file_list})
            else:
                file_list = self.relevance_info_dict.get(query_number)
                file_list.append(file_name)
                self.relevance_info_dict.update({query_number: file_list})
        fr.close()

    def get_relevant_docs(self, query_number):
        return self.relevance_info_dict.get(query_number)

    def get_relevant_docs_number(self,query_number):
        return len(self.relevance_info_dict.get(query_number))

    def read_query_results(self, result_path):
        fr = open(result_path, 'r', encoding='utf-8')
        for line in fr.readlines():
            query_number = line[0:line.find(' ')]
            file_name = line[line.find('Q0 ') + 3:line.rfind(' ')]
            if self.query_result.get(query_number) is None:
                file_list = list()
                file_list.append(file_name)
                self.query_result.update({query_number: file_list})
            else:
                file_list = self.query_result.get(query_number)
                file_list.append(file_name)
                self.query_result.update({query_number: file_list})
        fr.close()

    def calculate_mean_average_precision(self):
        mean_sum = 0
        for query_number in self.query_result.keys():
            curr_viewed = 0
            curr_relevant = 0
            precision_list = list()
            relevant_list = self.relevance_info_dict.get(query_number)
            result_list = self.query_result.get(query_number)
            if relevant_list is None:
                print("query" + query_number + "doesn't have relevance judgement")
            else:
                for i in range(0, len(result_list)):
                    result = result_list[i]
                    curr_viewed += 1
                    if result in relevant_list:
                        curr_relevant += 1
                        precision = curr_relevant / curr_viewed
                        precision_list.append(precision)
                summation = 0
                relevant_num = len(precision_list)
                for precision in precision_list:
                    summation += precision
                average_precision = summation / relevant_num
                mean_sum += average_precision
        mean_average_precision = mean_sum / len(self.relevance_info_dict.keys())
        return mean_average_precision

    def get_precision_table(self, query_number):
        precision_dict = dict()
        curr_relevant = 0
        result_list = self.query_result.get(query_number)
        relevant_list = self.relevance_info_dict.get(query_number)
        if relevant_list is None:
            print("query doesn't have relevance judgement")
        else:
            for i in range(0, len(result_list)):
                rank = i + 1
                result = result_list[i]
                if result in relevant_list:
                    curr_relevant += 1
                precision = curr_relevant / rank
                precision_dict.update({rank: precision})
            return precision_dict

    def get_recall_table(self, query_number):
        recall_dict = dict()
        curr_relevant = 0
        result_list = self.query_result.get(query_number)
        relevant_list = self.relevance_info_dict.get(query_number)
        if relevant_list is None:
            print("query doesn't have relevance judgement")
        else:
            relevant_num = len(relevant_list)
            for i in range(0, len(result_list)):
                rank = i+1
                result = result_list[i]
                if result in relevant_list:
                    curr_relevant += 1
                recall = curr_relevant / relevant_num
                recall_dict.update({rank:recall})
            return recall_dict

    def calculate_mean_reciprocal_rank(self):
        mean_reciprocal = 0
        query_numbers = len(self.relevance_info_dict.keys())
        for query_number in self.query_result.keys():
            relevant_list = self.relevance_info_dict.get(query_number)
            result_list = self.query_result.get(query_number)
            if relevant_list is None:
                print("query" + query_number + "doesn't have relevance judgement")
            else:
                for i in range(0, len(result_list)):
                    rank = i + 1
                    result = result_list[i]
                    if result in relevant_list:
                        reciprocal_rank = 1/rank
                        mean_reciprocal += reciprocal_rank
                        break
        mean_reciprocal_rank = mean_reciprocal / query_numbers
        return mean_reciprocal_rank

    def precision_at_k(self, k):
        precision_dict = dict()
        for query_number in self.query_result.keys():
            result_list = self.query_result.get(query_number)
            relevant_list = self.relevance_info_dict.get(query_number)
            if relevant_list is None:
                print("query" + query_number + "doesn't have relevance judgement")
            else:
                precision = 0
                for i in range(0, k):
                    result = result_list[i]
                    if result in relevant_list:
                        precision += 1
                precision = precision / k
                precision_dict.update({query_number: precision})
        return precision_dict
