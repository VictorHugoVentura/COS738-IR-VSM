# COS738-IR-VSM
Implementação de um sistema de recuperação em memória segundo o modelo vetorial.

Módulos:
--
1. processador.py - Processador de consultas.
2. gerador.py - Gerador de lista invertida.
3. indexador.py - Cria o modelo vetorial.
4. buscador.py - Buscador, responsável pelos resultados finais.

Arquivos gerados pelo sistema
--
1. consultas.csv - Criado pelo processador, lista todas as consultas processadas.
2. esperados.csv - Criado pelo processador, lista número do documento e seu número de votos.
3. gli.csv - Criado pelo gerador, cada linha correponde a uma plavra e à lista de documentos que a palavra aparece.
4. modelo.csv - Criado pelo indexador, especificado no arquivo modelo.txt.
5. resultados.csv - Criado pelo buscador, para cada consulta listamos o rank e o índice dos seus 5 documentos mais similares e o grau de similaridade para cada documento.

Como executar
--
Os módulos devem ser executados na ordem 1 -> 2 -> 3 -> 4. Se os arquivos da pasta results já foram gerados, os módulos podem ser executados em qualquer ordem.
