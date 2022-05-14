'''
A função desse módulo é criar as listas invertidas simples.

1) O Gerador Lista Invertida deverá ler um arquivo de configuração
    a. O nome do arquivo é GLI.CFG
    b. Ele contém dois tipos de instruções
        i. LEIA=<nome de arquivo>
        ii. ESCREVA=<nome de arquivo>
        iii. Podem ser uma ou mais instruções LEIA
        iv. Deve haver uma e apenas uma instrução ESCREVA
        v. A instrução ESCREVA aparece depois de todas as instruções LEIA
2) O Gerador Lista Invertida deverá ler um conjunto de arquivos em formato XML 
    a. Os arquivos a serem lidos serão indicados pela instrução LEIA no arquivo de configuração
    b. O formato é descrito pelo arquivo cfc2.dtd.
    c. O conjunto de arquivos será definido por um arquivo de configuração
    d. Os arquivos a serem lidos são os fornecidos na coleção
3) Só serão usados os campos RECORDNUM, que contém identificador do texto e ABSTRACT, que contém o texto 
a ser classificado
    a. Atenção: Se o registro não contiver o campo ABSTRACT deverá ser usado o campo EXTRACT
4) O Gerador Lista Invertida deverá gerar um arquivo
    a. O arquivo a ser gerado será indicado na instrução ESCREVA do arquivo de configuração
    b. O arquivo deverá ser no formato cvs
        i. O caractere de separação será o “;”, ponto e vírgula
    c. Cada linha representará uma palavra
    d. O primeiro campo de cada linha conterá a palavra em letras maiúsculas, sem acento
    e. O segundo campo de cada linha apresentará uma lista (Python) de identificadores de documentos 
onde a palavra aparece
    f. Se uma palavra aparece mais de uma vez em um documento, o número do documento aparecerá o 
mesmo número de vezes na lista
    g. Exemplo de uma linha
        i. FIBROSIS ; [1,2,2,3,4,5,10,15,21,21,21]
'''

import os
import re
import csv
import logging
import xml.etree.ElementTree as ET

from collections import defaultdict


FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename="logs/gerador.log", level=logging.INFO, format=FORMAT, encoding='utf-8')

def read():
    logging.info(f'Executando {__file__}')
    min_length = 2
    conf_file = 'gli.cfg'

    with open(f"config/{conf_file}") as config_file:
        logging.info(f'Abrindo {conf_file}')
        gli_dict = defaultdict(list)
        
        for line in config_file:
            line = line.rstrip()

            if line == "STEMMER":
                logging.info("Escolhida a opção de fazer stemming das palavras")
                from nltk.stem import PorterStemmer
                ps = PorterStemmer()
                stem = True
                continue
            elif line == "NOSTEMMER":
                stem = False
                continue

            instruct, filename = line.split('=')

            if instruct == "LEIA":
                with open(filename) as xml_file:
                    logging.info(f'Processando {filename}')
                    tree = ET.parse(xml_file)
                    root = tree.getroot()
                    
                    for record in root:
                        record_num = int(record.find("RECORDNUM").text)
                        
                        text_elem = record.find("ABSTRACT")
                        if text_elem is None:
                            text_elem = record.find("EXTRACT")
                            
                        if text_elem is not None:
                            words = text_elem.text
                            words = re.sub('[^a-zA-Z]', ' ', words)
                            words = words.split()
                            if stem:
                                words = [ps.stem(word).upper() for word in words if len(word) >= min_length]
                            else:
                                words = [word.upper() for word in words if len(word) >= min_length]
                            for word in words:
                                gli_dict[word].append(record_num)
            elif instruct == "ESCREVA":
                return filename, gli_dict
            else:
                logging.error(f"Erro ao ler {conf_file}")

def write(filename, gli_dict):
    with open(filename, 'w', newline='') as csv_file:
        logging.info(f'Abrindo {filename}')

        writer = csv.writer(csv_file, delimiter=";")
        writer.writerow(["Word", "Documents"])

        lines_written = 0        
        for key, value in sorted(gli_dict.items()):
            writer.writerow([key, value])
            lines_written += 1

            if lines_written % 100 == 0:
                logging.info(f'{lines_written} linhas escritas em {filename}')
        
        logging.info(f'{lines_written} linhas escritas em {filename}')
        logging.info(f'Fechando {filename}')

def main():
    filename, gli_dict = read()
    write(filename, gli_dict)

if __name__ == "__main__":
    main()
