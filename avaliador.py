import os
import ast
import logging
import numpy as np
import matplotlib.pyplot as plt

from processador import main as processador
from gerador import main as gerador
from indexador import main as indexador
from buscador import main as buscador

from metricas import (
    get_esperados_dict, get_interpolated_avg_precision,
    get_precision_at_k, get_recall_at_k,
    get_mean_reciprocal_rank, get_discounted_cumulative_gain
)


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

def graphing_function(x, y, xlabel, ylabel, title):
    plt.plot(x, y, "ro", markersize=3)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def histogram_func(x, y, num_bins):
    bins = np.linspace(0, 1, num_bins)
    plt.style.use('seaborn-deep')
    plt.hist([x, y], bins, label=['stemmer', 'nostemmer'])
    plt.legend(loc='upper right')
    plt.xlabel("R-precision")
    plt.ylabel("Número de consultas")
    plt.show()

def avaliador(stem):
    if stem:
        logger.info("Começando execução com stemmer")
    else:
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
    
    if stem:
        logger.info("Terminando execução com stemmer")
    else:
        logger.info("Terminando execução sem stemmer")

if __name__ == '__main__':
    num_of_queries = 100
    num_of_docs = 1239

    stem = False
    #avaliador(stem)
    esperados_dict = get_esperados_dict()

    # 1. Gráfico de 11 pontos de precisão e recall
    interpolated_avg_precision, thresholds, avg_precision = get_interpolated_avg_precision(stem, esperados_dict)

    graphing_function(thresholds,
                    interpolated_avg_precision,
                    "Revocação",
                    "Precisão",
                    "Gráfico de 11 pontos de precisão média interpolada")

    # 2. Precision@5    
    precision_5 = get_precision_at_k(stem, esperados_dict, 5)

    graphing_function(range(num_of_queries - 1),
                    precision_5,
                    "Consultas",
                    "Precisão",
                    "Precision@5")
    
    # 3. Precision@10
    precision_10 = get_precision_at_k(stem, esperados_dict, 10)

    graphing_function(range(num_of_queries - 1),
                    precision_10,
                    "Consultas",
                    "Precisão",
                    "Precision@10")

    # 4. F1
    recall_10 = get_recall_at_k(stem, esperados_dict, 10)
    f1_score = 2/(1/precision_10 + 1/recall_10)

    graphing_function(range(num_of_queries - 1),
                    f1_score,
                    "Consultas",
                    "F1",
                    "F1 score")

    # 5. Histograma de R-Precision (comparativo)
    r_precision_stemmer = get_recall_at_k(True, esperados_dict, r_precision=True)
    r_precision_nostemmer = get_recall_at_k(False, esperados_dict, r_precision=True)
    histogram_func(r_precision_stemmer, r_precision_nostemmer, 30)

    # 6. MAP
    print("MAP:", np.mean(avg_precision))

    # 7. MRR
    print("MRR:", get_mean_reciprocal_rank(stem, esperados_dict))

    # 8. Discounted Cumulative Gain (médio)
    mean_cumulative_gain = get_discounted_cumulative_gain(stem, esperados_dict, 10)

    graphing_function(range(10),
                mean_cumulative_gain,
                "Rank das consultas",
                "DCG",
                "Discounted Cumulative Gain (médio)")

    # 9. Normalized Discounted Cumulative Gain
