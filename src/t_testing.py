from src.Ttest import TTestModel

model = TTestModel(significant_level=0.05, data='p')
model.set_base_engine('../results/Evaluation_tf-idf baseline result.txt')       #A
test_result = model.set_test_engine('../results/Evaluation_BM25 baseline result.txt')           #B
model.calculate_t_test_p_value(test_result)
