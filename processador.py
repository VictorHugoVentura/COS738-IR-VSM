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

import re
import csv
import xml.etree.ElementTree as ET

with open("config/pc.cfg") as config_file:
    for i, line in enumerate(config_file):
        if i == 0:
            leia = line.split('=')[1].rstrip()
        elif i == 1:
            consultas = line.split('=')[1].rstrip()
        elif i == 2:
            esperados = line.split('=')[1].rstrip()
    
with open(leia) as xml_file, \
    open(consultas, "w", newline='') as consulta_f, \
    open(esperados, "w", newline='') as esperado_f:
    tree = ET.parse(xml_file)
    root = tree.getroot()

    consulta_w = csv.writer(consulta_f, delimiter=";")
    consulta_w.writerow(["QueryNumber", "QueryText"])
    
    esperado_w = csv.writer(esperado_f, delimiter=";")
    esperado_w.writerow(["QueryNumber", "DocNumber", "DocVotes"])
    
    for query in root:
        number = query.find("QueryNumber")
        text = query.find("QueryText")
        processed_text = re.sub('[^A-Z]', ' ', text.text.upper())
        consulta_w.writerow([number.text, processed_text])
        
        records = query.find("Records")
        for item in records:
            score = item.attrib['score']
            
            s = 0
            for x in score:
                if x != "0":
                    s += 1
            
            esperado_w.writerow([number.text, item.text, s])