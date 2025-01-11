# Whoosh Search Engine

Este repositório apresenta um motor de busca criado com Whoosh, implementando diversas técnicas para melhorar a indexação e a recuperação de informações.

## Principais Técnicas

1. **Indexação**:

   - Remoção de stopwords para reduzir ruídos e melhorar a relevância dos documentos.

2. **Pré-processamento da Consulta**:

   - Tokenização para dividir a consulta em palavras significativas.
   - Remoção de stopwords para focar nos termos importantes.

3. **Extração de Subconsultas**:

   - Aplicação de pesos nas palavras da consulta para priorizar termos mais relevantes.

4. **Expansão de Subconsultas**:

   - Utilização de sinônimos para enriquecer a consulta e melhorar a cobertura de resultados.

## Como usar

1. Baixe o dataset desejado a partir do [link de download]([https://example.com/dataset](https://www.dropbox.com/scl/fi/0nrrbvh9rs2zo8magsoww/pan-plagiarism-corpus-2011.zip?rlkey=nrb7i7ko8vbze76gppnq6k41n&e=2&st=hdko4hxx&dl=0)) e salve na mesma pasta do projeto com o nome `dataset`.

2. Rode o script de indexação para preparar o índice:

   ```bash
   python indexacao.py
   ```

3. Em seguida, execute o script para realizar consultas:

   ```bash
   python consultas.py
   ```
