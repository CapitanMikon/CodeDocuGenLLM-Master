from langchain_ollama import OllamaEmbeddings
from Exceptions import ExtNotSupported


def get_embedding_function():
    return OllamaEmbeddings(model="nomic-embed-text")


def get_language_by_ext(ext):
    if ext == ".java":
        return "Java"
    elif ext == ".js":
        return "JavaScript"
    else:
        raise ExtNotSupported(ext)
