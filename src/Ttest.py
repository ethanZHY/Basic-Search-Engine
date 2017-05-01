'''
Model examine whether the difference of performance of two search engines are statistically significant using t-test
'''

from scipy import stats
import math


class TTestModel:
    significant_level = 0
    base_engine_statistics = dict()
    data = ''
    '''
    constructor set the significant level(typically 0.05,0.1) and data is the value to test with:
    'p' for precision
    'r' for reciprocal rank
    '''
    def __init__(self, significant_level, data):
        self.significant_level = significant_level
        self.data = data

    '''
    set the default search engine A
    result path is the path of A's evaluation result
    '''
    def set_base_engine(self, result_path):
        fr = open(result_path)
        line = fr.readline()
        while line != '':
            if line.find('Query:') != -1:
                query_num = line[line.find(":")+1:]
                sum = 0
                flag = 0
                line = fr.readline()
                while line.find(self.data + ' =') != -1:
                    flag += 1
                    # get precision value
                    if self.data == 'p':
                        sum += float(line[line.find(self.data + ' =')+4:line.find('r =')-1])
                    # get reciprocal value
                    if self.data == 'r':
                        sum += float(line[line.find(self.data + ' =') + 4:])
                    line = fr.readline()
                value = sum/100
                if value != 0 or flag != 0:
                    self.base_engine_statistics.update({query_num: value})  # store the average value
            else:
                line = fr.readline()

    '''
    set the examine search engine B
    result path is the path of B's evaluation result
    '''
    def set_test_engine(self, result_path):
        test_engine_statistics = dict()
        fr = open(result_path)
        line = fr.readline()
        while line != '':
            if line.find('Query:') != -1:
                query_num = line[line.find(":") + 1:]
                sum = 0
                flag = 0
                line = fr.readline()
                while line.find(self.data + ' =') != -1:
                    flag += 1
                    if self.data == 'p':
                        sum += float(line[line.find(self.data + ' =') + 4:line.find('r =') - 1])
                    if self.data == 'r':
                        sum += float(line[line.find(self.data + ' =') + 4:])
                    line = fr.readline()
                value = sum / 100
                if value != 0 or flag != 0:
                    test_engine_statistics.update({query_num: value})
            else:
                line = fr.readline()
        return test_engine_statistics

    # calculate t-test value and corresponding p-value
    def calculate_t_test_p_value(self, test_engine_statistics):
        diff_list = list()
        n = len(self.base_engine_statistics.keys())
        sum = 0
        for num in self.base_engine_statistics.keys():
            a = self.base_engine_statistics.get(num)
            b = test_engine_statistics.get(num)
            diff = b-a
            diff_list.append(diff)
            sum += diff
        mean = sum / n
        derivation = 0
        for diff in diff_list:
            derivation += math.pow((diff-mean), 2) / n
        derivation = math.sqrt(derivation)
        t_value = mean/derivation * math.sqrt(n)
        print(t_value)
        p_value = stats.t.sf(abs(t_value), n-1)  # one-tailed
        print(p_value)
