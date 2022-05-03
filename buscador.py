'''
O objetivo desse módulo é obter os resultados de um conjunto de buscas em um modelo salvo.

1) O Buscador deverá ler o arquivo de consultas e o arquivo do modelo vetorial e realizar cada consulta, 
escrevendo outro arquivo com a resposta encontrada para cada consulta.
2) Para isso, usará o arquivo de configuração BUSCA.CFG, que possuirá duas instruções
    a. MODELO=<nome de arquivo>
    b. CONSULTAS=<nome de arquivo>
    c. RESULTADOS=<nome de arquivo>
3) A busca deverá ser feita usando modelo vetorial
4) Cada palavra na consulta terá o peso 1
5) O arquivo de resultados deverá
    a. Ser no formato .csv
    b. Separar os campos por “;”, ponto e vírgula
    c. Cada uma de suas linhas terá dois campos
        i. O primeiro contendo o identificador da consulta
        ii. O segundo contendo uma lista Python de ternos ordenados
            1. O primeiro elemento é a posição do documento no ranking
            2. O segundo elemento é o número do documento
            3. O terceiro elemento é a distância do elemento para a consulta
'''

import csv
from collections import Counter

min_length = 2
user_input = int(input("Press 1 for dot product similarity,\nPress 2 for cosine similarity (significantly slower)\n"))

with open("config/busca.cfg") as config_file:
    for i, line in enumerate(config_file):
        if i == 0:
            modelo = line.split('=')[1].rstrip()
        elif i == 1:
            consultas = line.split('=')[1].rstrip()
        elif i == 2:
            resultados = line.split('=')[1].rstrip()

matrix_dict = {}

with open(modelo) as model_file:
    model_reader = csv.reader(model_file, delimiter=";")
    next(model_reader)
    
    for line in model_reader:
        if line[0] not in matrix_dict.keys():
            matrix_dict[line[0]] = {int(line[1]): float(line[2])}
        else:
            matrix_dict[line[0]][int(line[1])] = float(line[2])


with open(resultados, "w", newline='') as result_file:
    writer = csv.writer(result_file, delimiter=";")
    writer.writerow(["QueryNumber", "[DocRanking, DocNumber, Similarity]"])

with open(consultas) as query_file:
    query_reader = csv.reader(query_file, delimiter=";")
    next(query_reader)
    
    for query in query_reader:
        query_dict = {}
        
        words = query[1].split()
        words = [word for word in words if len(word) >= min_length]
        query_vec = Counter(words)
        
        for word in query_vec:
            if word in matrix_dict.keys():
                current_dict = matrix_dict[word]
                weight_list = []
                for key in current_dict:
                    weight_list.append(current_dict[key])
                    if key not in query_dict:
                        query_dict[key] = current_dict[key] * query_vec[word]
                    else:
                        query_dict[key] += current_dict[key] * query_vec[word]
                
                # similaridade por cosseno
                if user_input == 2:
                    import numpy as np
                    for key in current_dict:
                        query_dict[key] /= np.linalg.norm(list(query_vec.values())) * np.linalg.norm(weight_list)
        
        
        sorted_values = sorted(query_dict.items(), key=lambda item: item[1], reverse=True)[:5]
        
        with open(resultados, "a", newline='') as result_file:
            result_writer = csv.writer(result_file, delimiter=";")
            for i, elem in enumerate(sorted_values):
                li = [i + 1, sorted_values[i][0], sorted_values[i][1]]
                result_writer.writerow([query[0], li])