'''
O objetivo desse módulo é transformar o arquivo de consultas fornecido ao padrão de palavras que estamos utilizando.

1) O Processador de Consultas deverá ler um arquivo de configuração
    a. O arquivo é criado por vocês
    b. O nome do arquivo é PC.CFG
    c. Ele contém dois tipos de instruções
        i. LEIA=<nome de arquivo>
        ii. CONSULTAS=<nome de arquivo>
        iii. ESPERADOS=<nome de arquivo>
        iv. As instruções são obrigatórias, aparecem uma única vez e nessa ordem.
2) O Processador de Consultas deverá ler um arquivo em formato XML 
    a. O arquivo a ser lido será indicado pela instrução LEIA no arquivo de configuração
        i. O formato é descrito pelo arquivo “cfc2-query.dtd”.
        ii. O arquivo a ser lido é “cfquery.xml”.
3) O Processador de Consultas deverá gerar dois arquivos 
    a. Os arquivos deverão ser no formato cvs
        i. O caractere de separação será o “;”, ponto e vírgula
            1. Todos os caracteres “;” que aparecerem no arquivo original devem ser eliminados
        ii. A primeira linha do arquivo cvs deve ser o cabeçalho com o nome dos campos
    b. O primeiro arquivo a ser gerado será indicado na instrução CONSULTAS do arquivo de configuração
        i. Cada linha representará uma consulta
            1. O primeiro campo de cada linha conterá o número da consulta
                a. Campo QueryNumber
            2. O segundo campo de cada linha conterá uma consulta processada em letras maiúsculas, sem acento
                a. A partir do campo QueryText
            3. Cada aluno poderá escolher como criar sua consulta
    c. O segundo arquivo a ser gerado será indicado na instrução ESPERADOS
        i. Cada linha representará uma consulta
            1. O primeiro campo de cada linha conterá o número da consulta
                a. Campo QueryNumber
            2. O segundo campo conterá um documento
                a. Campo DocNumber
            3. O terceiro campo conterá o número de votos do documento
                a. Campo DocVotes
            4. Uma consulta poderá aparecer em várias linhas, pois podem possuir vários documentos como resposta
            5. As linhas de uma consulta devem ser consecutivas no arquivo
            6. Essas contas devem ser feitas a partir dos campos Records, Item e do atributo Score de Item
                a. Considerar qualquer coisa diferente de zero como um voto
'''

import os
import re
import csv
import logging
import xml.etree.ElementTree as ET


os.makedirs('logs', exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('logs/processador.log', encoding='utf-8')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def processador():
    logger.info(f'Executando {__file__}')
    conf_file = "pc.cfg"

    with open(f"config/{conf_file}") as config_file:
        logger.info(f'Abrindo {conf_file}')

        for i, line in enumerate(config_file):
            line = line.rstrip()

            if line == "STEMMER":
                logger.info("Escolhida a opção de fazer stemming das consultas")
                from nltk.stem import PorterStemmer
                ps = PorterStemmer()
                stem = True
                continue
            elif line == "NOSTEMMER":
                stem = False
                continue

            instruct, filename = line.split('=')

            if instruct == "LEIA":
                leia = filename
            elif instruct == "CONSULTAS":
                consultas = filename
            elif instruct == "ESPERADOS":
                esperados = filename
            else:
                logging.error(f'Erro ao ler {conf_file}')
        
    with open(leia) as xml_file, \
        open(consultas, "w", newline='') as consulta_f, \
        open(esperados, "w", newline='') as esperado_f:
        logger.info(f"Abrindo {leia}, {consultas} e {esperados}")
        tree = ET.parse(xml_file)
        root = tree.getroot()

        consulta_w = csv.writer(consulta_f, delimiter=";")
        consulta_w.writerow(["QueryNumber", "QueryText"])
        
        esperado_w = csv.writer(esperado_f, delimiter=";")
        esperado_w.writerow(["QueryNumber", "DocNumber", "DocVotes"])
        
        lines_read = 0
        lines_written_consulta = 0
        lines_written_esperado = 0

        for query in root:
            lines_read += 1
            lines_written_consulta += 1
            if lines_read % 10 == 0:
                logger.info(f"{lines_read} consultas processadas de {leia}")
                logger.info(f"{lines_written_consulta} linhas escritas em {consultas}")
            
            query_number = query.find("QueryNumber")
            query_text = query.find("QueryText")
            processed_text = re.sub('[^a-zA-Z]', ' ', query_text.text)

            if stem:
                processed_text = ' '.join(ps.stem(word) for word in processed_text.split())

            consulta_w.writerow([query_number.text, processed_text.upper()])
            
            records = query.find("Records")
            for item in records:
                lines_written_esperado += 1
                score = item.attrib['score']
                
                s = 0
                for x in score:
                    if x != "0":
                        s += 1
                
                esperado_w.writerow([query_number.text, item.text, s])

                if lines_written_esperado % 100 == 0:
                    logger.info(f"{lines_written_esperado} linhas escritas em {esperados}")

        logger.info(f"{lines_read} consultas processadas de {leia}")
        logger.info(f"{lines_written_consulta} linhas escritas em {consultas}")
        logger.info(f"{lines_written_esperado} linhas escritas em {esperados}")
        logger.info(f"Fechando {leia}, {consultas} e {esperados}")

def main():
    processador()

if __name__ == "__main__":
    main()
