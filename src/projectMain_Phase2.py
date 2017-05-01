from src.RelevanceJudgement2 import Evaluation

print('Phase 2:')
evaluation = Evaluation()
relevance_path = "../cacm_rel.txt"


file_path = "../result/baseline/BM25_baseline.txt"
path = file_path[:file_path.find('/', 10)+1]
text_file_name = file_path[file_path.find('/', 10)+1:]
evaluation.main(relevance_path=relevance_path,
                path=path, text_file_name=text_file_name)
