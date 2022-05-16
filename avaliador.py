import os
import ast
import logging
import numpy as np
import matplotlib.pyplot as plt

from collections import defaultdict
from sklearn.metrics import precision_recall_curve

from processador import main as processador
from gerador import main as gerador
from indexador import main as indexador
from buscador import main as buscador


os.makedirs('logs', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/avaliador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def stemmer_option(stem):
    with open("config/pc.cfg") as pc_config, \
        open("config/gli.cfg") as gli_config, \
        open("config/busca.cfg") as busca_config:
        pc_lines = pc_config.readlines()
        gli_lines = gli_config.readlines()
        busca_lines = busca_config.readlines()

        if stem:
            pc_lines[0] = "STEMMER\n"
            gli_lines[0] = "STEMMER\n"
            busca_lines[0] = "STEMMER\n"
        else:
            pc_lines[0] = "NOSTEMMER\n"
            gli_lines[0] = "NOSTEMMER\n"
            busca_lines[0] = "NOSTEMMER\n"

    with open("config/pc.cfg", "w") as pc_config, \
        open("config/gli.cfg", "w") as gli_config, \
        open("config/busca.cfg", "w") as busca_config:
        pc_config.writelines(pc_lines)
        gli_config.writelines(gli_lines)
        busca_config.writelines(busca_lines)

def grafico_11_pontos(stem):
    if stem:
        results_path = "results/resultados-stemmer.csv"
    else:
        results_path = "results/resultados-nostemmer.csv"

    thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    with open("results/esperados.csv") as esperados:
        next(esperados)
        d = defaultdict(list)

        for line in esperados:
            line = line.rstrip()
            query_num, doc_num, _ = line.split(";")

            d[int(query_num)].append(int(doc_num))

    with open(results_path) as resultados:
        next(resultados)
        Y = np.zeros((100, 1239))
        probs = np.zeros((100, 1239))

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

    graph_array = np.zeros((100, 11))
    thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    for i in range(100):
        precision, recall, _ = precision_recall_curve(Y[i], probs[i])
        precision = precision[::-1]
        recall = recall[::-1]
        for j, threshold in enumerate(thresholds):
            graph_array[i][j] = precision[np.argmax(recall >= threshold)]
    
    graph_array = np.delete(graph_array, 92, 0) # query 93 is missing
    graph_array = np.mean(graph_array, axis=0)

    plt.plot(thresholds, graph_array, "ro", markersize=3)
    plt.title("Gráfico de 11 pontos de precisão média interpolada")
    plt.xlabel("Revocação")
    plt.ylabel("Precisão")
    plt.show()

def avaliador(stem):
    logger.info("Começando execução sem stemmer")
    stemmer_option(stem)

    logger.info("Executando processador")
    processador()
    logger.info("Executando gerador")
    gerador()
    logger.info("Executando indexador")
    indexador()
    logger.info("Executando buscador")
    buscador()
    logger.info("Terminando execução sem stemmer")

    logger.info("Fazendo gráfico de 11 pontos de precisão média interpolada")
    grafico_11_pontos(stem)

if __name__ == '__main__':

    avaliador(False)
