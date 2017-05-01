'''
main process to run evaluation
'''

from src.RelevanceJudgeModel2 import EvaluationModel


class Evaluation:
    def main(self, relevance_path, path, text_file_name):
        path = path
        BM25_baseline = EvaluationModel(relevance_path)
        BM25_baseline.run(path, text_file_name)

