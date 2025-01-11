import glob
import os
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer


def preprocessamento(conteudo):
    tokens = word_tokenize(conteudo)

    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word.lower() not in stop_words]

    return " ".join(tokens)


def criar_indice(index_path="indexdir"):
    schema = Schema(title=TEXT(stored=True), content=TEXT,
                    path=ID(stored=True, unique=True))
    if not os.path.exists(index_path):
        os.mkdir(index_path)
    return create_in(index_path, schema)


def carregar_documentos(diretorio_base):
    documentos = []
    for filepath in glob.glob(f"{diretorio_base}/**/*.txt", recursive=True):
        with open(filepath, "r", encoding="utf-8") as file:
            conteudo = file.read()
            conteudo_processado = preprocessamento(conteudo)
            documentos.append({
                "title": os.path.basename(filepath),
                "content": conteudo_processado,
                "path": filepath
            })
    return documentos


def popular_indice(index, documentos):
    writer = index.writer()
    for doc in documentos:
        writer.add_document(
            title=doc["title"],
            content=doc["content"],
            path=doc["path"]
        )
    writer.commit()
    print(f"{len(documentos)} documentos adicionados ao índice!")


def buscar_no_indice(consulta, index_path="indexdir"):
    index = os.open_dir(index_path)
    with index.searcher() as searcher:
        query = QueryParser("content", index.schema).parse(consulta)
        resultados = searcher.search(query)
        for resultado in resultados:
            print(f"Título: {resultado['title']}")
            print(f"Caminho: {resultado['path']}")
            print("-" * 40)


if __name__ == "__main__":
    diretorio_base = "dataset/external-detection-corpus/suspicious-document"
    index_dir = "indexdir"

    documentos = carregar_documentos(diretorio_base)
    if documentos:
        index = criar_indice(index_dir)
        popular_indice(index, documentos)
