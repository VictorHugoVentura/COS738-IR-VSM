'''
A função desse módulo é criar o modelo vetorial, dadas as listas invertidas simples.

1) O indexador será configurado por um arquivo INDEX.CFG
    a. O arquivo conterá apenas uma linha LEIA, que terá o formato
        i. LEIA=<nome de arquivo>
    b. O arquivo conterá apenas uma linha ESCREVA, que terá o formato
        i. ESCREVA=<nome de arquivo>
2) O Indexador deverá implementar um indexador segundo o Modelo Vetorial
    a. O Indexador deverá utilizar o tf/idf padrão
        i. O tf pode ser normalizado como proposto na equação 2.1 do Cap. 2 do Modern Information Retrieval
    b. O indexador deverá permitir a alteração dessa medida de maneira simples
    c. O Indexador deverá possuir uma estrutura de memória deve de alguma forma representar a matriz termo documento
    d. O Indexador deverá classificar toda uma base transformando as palavras apenas da seguinte forma:
        i. Apenas palavras de 2 letras ou mais
        ii. Apenas palavras com apenas letras
        iii. Todas as letras convertidas para os caracteres ASCII de A até Z, ou seja, só letras maiúsculas e nenhum outro símbolo
    e. A base a ser indexada estará na instrução LEIA do arquivo de configuração
3) O sistema deverá salvar toda essa estrutura do Modelo Vetorial para utilização posterior
'''

import csv
import ast
import math

from collections import Counter

freq_input = int(input("Press 1 for raw frequency,\nPress 2 for relative frequency,\n"))

with open("config/index.cfg") as config_file:
    for i, line in enumerate(config_file):
        if i == 0:
            leia = line.split('=')[1].rstrip()
        elif i == 1:
            escreva = line.split('=')[1].rstrip()

num_words_list = []
vocab = 0

with open(leia, newline='\n') as csv_file:
    reader = csv.reader(csv_file, delimiter=";")
    next(reader)
    
    for line in reader:
        li = ast.literal_eval(line[1])
        vocab += 1
        
        for elem in li:
            while elem > len(num_words_list):
                num_words_list.append(0)
            num_words_list[elem - 1] += 1
        

num_docs = len(num_words_list)

with open(leia, newline='\n') as read_file, \
    open(escreva, "w", newline='') as write_file:
    reader = csv.reader(read_file, delimiter=";")
    next(reader)
    
    writer = csv.writer(write_file, delimiter=";")
    writer.writerow(["Word", "DocNumber", "Weight"])
    
    for line in reader:
        li = ast.literal_eval(line[1])
        c = Counter(li)
        for doc in c:
            if freq_input == 1:
                weight = c[doc] * math.log(num_docs/len(set(li)) + 1)
            elif freq_input == 2:
                weight = (c[doc]/num_words_list[doc - 1]) * math.log(num_docs/len(set(li)) + 1)
            writer.writerow([line[0], doc, weight])