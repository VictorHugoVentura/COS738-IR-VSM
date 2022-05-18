import ast
import numpy as np

from math import log2
from collections import defaultdict
from sklearn.metrics import precision_recall_curve, average_precision_score


num_of_queries = 100
num_of_docs = 1239
missing_query = 92 # query 93 is missing

def get_esperados_dict(votes=False):
    with open("results/esperados.csv") as esperados:
        next(esperados)
        if votes:
            d = defaultdict(lambda: ([], []))
        else:
            d = defaultdict(list)

        for line in esperados:
            line = line.rstrip()
            query_num, doc_num, doc_votes = line.split(";")

            if votes:
                d[int(query_num)][0].append(int(doc_num))
                d[int(query_num)][1].append(int(doc_votes))
            else:
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

def get_recall_at_k(stem, d, k=10, r_precision=False):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"
    
    with open(results_path) as resultados:
        next(resultados)
        recall = np.zeros(num_of_queries)

        for line in resultados:
            line = line.rstrip()
            query_num, results_list = line.split(";")
            query_num = int(query_num)
            results_list = ast.literal_eval(results_list)
            
            if r_precision:
                if results_list[0] >= len(d[query_num]):
                    continue
            else:
                if results_list[0] >= k:
                    continue

            if results_list[1] in d[query_num]:
                recall[query_num - 1] += 1
        
        for i in d.keys():
            recall[i - 1] /= len(d[i])

        recall = np.delete(recall, missing_query)
        return recall

def get_mean_reciprocal_rank(stem, d):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"

    with open(results_path) as resultados:
        next(resultados)
        reciprocal_rank = np.zeros(num_of_queries)

        for line in resultados:
            line = line.rstrip()
            query_num, results_list = line.split(";")
            query_num = int(query_num)
            results_list = ast.literal_eval(results_list)
        
            if reciprocal_rank[query_num - 1] == 0 and results_list[1] in d[query_num]:
                reciprocal_rank[query_num - 1] = 1/(results_list[0] + 1)

    return np.mean(reciprocal_rank)

def get_discounted_cumulative_gain(stem, d, k):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"

    with open(results_path) as resultados:
        next(resultados)
        cumulative_gain = np.zeros((num_of_queries, k))
        s = 0
        
        for line in resultados:
            line = line.rstrip()
            query_num, results_list = line.split(";")
            query_num = int(query_num)
            results_list = ast.literal_eval(results_list)
            doc_rank, doc_num, _ = results_list

            if doc_rank >= k:
                continue

            if doc_num in d[query_num][0]:
                if doc_rank == 0:
                    s = 0

                doc_index = d[query_num][0].index(doc_num)
                s += d[query_num][1][doc_index]/log2(doc_rank + 2)

            cumulative_gain[query_num - 1][doc_rank] = s

    return np.mean(cumulative_gain, axis=0)
        
