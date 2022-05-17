import ast
import numpy as np

from collections import defaultdict
from sklearn.metrics import precision_recall_curve, average_precision_score


num_of_queries = 100
num_of_docs = 1239
missing_query = 92 # query 93 is missing

def get_esperados_dict():
    with open("results/esperados.csv") as esperados:
        next(esperados)
        d = defaultdict(list)

        for line in esperados:
            line = line.rstrip()
            query_num, doc_num, _ = line.split(";")

            d[int(query_num)].append(int(doc_num))
    return d

def get_interpolated_avg_precision(stem, d):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"

    with open(results_path) as resultados:
        next(resultados)
        Y = np.zeros((num_of_queries, num_of_docs))
        probs = np.zeros((num_of_queries, num_of_docs))

        for line in resultados:
            line = line.rstrip()
            query_num, results_list = line.split(";")
            query_num = int(query_num)
            results_list = ast.literal_eval(results_list)
            
            if results_list[1] in d[query_num]:
                Y[query_num - 1][results_list[0]] = 1
            else:
                Y[query_num - 1][results_list[0]] = 0
            
            probs[query_num - 1][results_list[0]] = results_list[2]

    graph_array = np.zeros((num_of_queries, 11))
    thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    avg_precision = np.zeros(num_of_queries)

    for i in range(num_of_queries):
        precision, recall, _ = precision_recall_curve(Y[i], probs[i])
        precision = precision[::-1]
        recall = recall[::-1]
        for j, threshold in enumerate(thresholds):
            graph_array[i][j] = precision[np.argmax(recall >= threshold)]
        
        avg_precision[i] = average_precision_score(Y[i], probs[i])
    
    graph_array = np.delete(graph_array, missing_query, 0)
    graph_array = np.mean(graph_array, axis=0)

    avg_precision = np.delete(avg_precision, missing_query, 0)

    return graph_array, thresholds, avg_precision

def get_precision_at_k(stem, d, k):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"
    
    with open(results_path) as resultados:
        next(resultados)
        precision = np.zeros(num_of_queries)

        for line in resultados:
            line = line.rstrip()
            query_num, results_list = line.split(";")
            query_num = int(query_num)
            results_list = ast.literal_eval(results_list)
            
            if results_list[0] >= k:
                continue

            if results_list[1] in d[query_num]:
                precision[query_num - 1] += 1
        
        precision /= k
        precision = np.delete(precision, missing_query)
        return precision

def get_recall_at_k(stem, d, k, r_precision=False):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"
    
    if r_precision:
        num_rel_docs = np.zeros(num_of_queries)
        for i, li in enumerate(d.values()):
            num_rel_docs[i] = len(li)
    
    with open(results_path) as resultados:
        next(resultados)
        recall = np.zeros(num_of_queries)

        for line in resultados:
            line = line.rstrip()
            query_num, results_list = line.split(";")
            query_num = int(query_num)
            results_list = ast.literal_eval(results_list)
            
            if r_precision:
                k = num_rel_docs[query_num - 1]
            
            if results_list[0] >= k:
                continue

            if results_list[1] in d[query_num]:
                recall[query_num - 1] += 1
        
        for i in range(1, num_of_queries + 1):
            recall[i - 1] /= len(d[i])

        recall = np.delete(recall, missing_query)
        return recall
