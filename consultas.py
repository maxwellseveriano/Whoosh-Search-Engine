import os
import glob
import re
import time
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh.qparser import OrGroup
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from collections import Counter
import matplotlib.pyplot as plt


def preprocessamento(conteudo):
    tokens = word_tokenize(conteudo)
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]
    return tokens


def extrair_subconsultas(tokens, limites=(100, 50, 20, 5)):

    frequencias = Counter(tokens)

    resultado = [[] for _ in limites]

    for word, freq in frequencias.items():
        for i, limite in enumerate(limites):
            if freq > limite:
                resultado[i].append(word)
                break

    return resultado


def expandir_subconsulta(subconsulta):
    sinonimos = []
    vetorSub = [elemento for linha in subconsulta for elemento in linha]
    for palavra in vetorSub:
        for syn in wordnet.synsets(palavra):
            for lemma in syn.lemmas():
                sinonimos.append(lemma.name().replace("_", " "))
    return list(set(sinonimos))


def buscar_no_indice(a, consulta_expandida, index_path="indexdir"):
    index = open_dir(index_path)
    resultados_relevantes = []
    with index.searcher() as searcher:
        a1 = " ".join(a[0][:50])
        a2 = " ".join(a[1][:50])
        a3 = " ".join(a[2][:50])
        a4 = " ".join(a[3][:50])
        a1 = re.sub(r'[^a-zA-Z ]', '', a1)
        a2 = re.sub(r'[^a-zA-Z ]', '', a2)
        a3 = re.sub(r'[^a-zA-Z ]', '', a3)
        a4 = re.sub(r'[^a-zA-Z ]', '', a4)
        consulta_reduzeida = " ".join(consulta_expandida[:50])
        query = QueryParser("content", index.schema).parse(
            f"({a1})^10 OR ({a2})^7 ({a3})^5 OR ({a4})^2 OR ({consulta_reduzeida})")
        resultados = searcher.search(query)
        for resultado in resultados:
            resultados_relevantes.append({
                "title": resultado["title"],
                "path": resultado["path"],
                "score": resultado.score
            })
    return resultados_relevantes


def calcular_precision_recall(resultados, documentos_relevantes, k_values=[2, 4, 6, 8, 10]):
    precision = []
    recall = []

    resultados = sorted(resultados, key=lambda x: x['score'], reverse=True)

    for fonte in resultados[:10]:
        print(f"   Caminho: {fonte['path']}")

    for k in k_values:
        top_k_resultados = resultados[:k]

        relevantes_encontrados = sum(
            1 for r in top_k_resultados if r['path'] in documentos_relevantes)

        p_k = relevantes_encontrados / k
        precision.append(p_k)

        r_k = relevantes_encontrados / len(documentos_relevantes)
        recall.append(r_k)

    return precision, recall


def plotar_precision_recall(k_values, precision, recall):
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.plot(k_values, precision, marker='o', linestyle='-', color='b')
    plt.title("Precision at k")
    plt.xlabel("k")
    plt.ylabel("Precision")
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(k_values, recall, marker='o', linestyle='-', color='r')
    plt.title("Recall at k")
    plt.xlabel("k")
    plt.ylabel("Recall")
    plt.grid(True)

    plt.tight_layout()
    plt.show()


path_encontrados = []


def detectar_plagio_avaliacao(diretorio_suspeito, index_path="indexdir"):
    arquivos_suspeitos = glob.glob(f"{diretorio_suspeito}/*.txt")

    index = open_dir(index_path)
    documentos_relevantes = ["suspicious-document00079.txt"]

    k_values = [2, 4, 6, 8, 10]

    melhores_resultados = []
    tempo_preproc = 0
    tempo_consul = 0
    for arquivo in arquivos_suspeitos:
        with open(arquivo, "r", encoding="utf-8") as file:
            conteudo = file.read()

            tempo_preproc_ini = time.time()
            tokens = preprocessamento(conteudo)
            tempo_preproc += (time.time() - tempo_preproc_ini)

            tempo_consul_ini = time.time()
            subconsultas = extrair_subconsultas(tokens)
            consulta_expandida = expandir_subconsulta(subconsultas)
            tempo_consul += (time.time() - tempo_consul_ini)

            resultados = buscar_no_indice(
                subconsultas, consulta_expandida, index_path)

            print(f"\nDocumento suspeito: {os.path.basename(arquivo)}")
            if resultados:
                print("Possível fonte de plágio encontrada:")
                print(f" - Título: {resultados[0]['title']}")
                print(f"   Caminho: {resultados[0]['path']}")
                print(f"   Similaridade: {resultados[0]['score']:.2f}")
                melhores_resultados.append(
                    {"score": resultados[0]['score'], "path": os.path.basename(arquivo)})

            else:
                print("Nenhum arquivo suspeito encontrado.")

    print(
        f"\n\nTempo medio de pre-processamento: {tempo_preproc/len(arquivos_suspeitos)}")
    print(f"Tempo medio de extracao: {tempo_consul/len(arquivos_suspeitos)}\n")

    precision, recall = calcular_precision_recall(
        melhores_resultados, documentos_relevantes, k_values)
    print("\nPrecision at k:", precision)
    print("Recall at k:", recall)

    plotar_precision_recall(k_values, precision, recall)


if __name__ == "__main__":
    diretorio_suspeito = "dataset/external-detection-corpus/suspicious-document/part1"
    index_dir = "indexdir"

    detectar_plagio_avaliacao(diretorio_suspeito, index_dir)
