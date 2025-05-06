from langchain_ollama import OllamaEmbeddings
import numpy as np
from numpy.linalg import norm
from nltk.translate.bleu_score import sentence_bleu

embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
)

text_by_human = "ada asasa asas as aaaaaaaaa"
text_by_ai = ""

def compare(human, ai):
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",
    )

    human_vector = embeddings.embed_query(human)
    ai_vector = embeddings.embed_query(ai)

    # print(str(human_vector))
    # print(str(ai_vector))
    cosine = np.dot(human_vector, ai_vector) / (norm(human_vector) * norm(ai_vector))
    print([[x.translate(str.maketrans({',': '', '.': ''})) for x in human.split(" ")]])
    print([x.translate(str.maketrans({',': '', '.': ''})) for x in ai.split(" ")])
    bleu_score = sentence_bleu([[x.translate(str.maketrans({',': '', '.': ''})) for x in human.split(" ")]], [x.translate(str.maketrans({',': '', '.': ''})) for x in ai.split(" ")])
    print("Cosine Similarity:", cosine)
    print("Bleu score:", bleu_score)


compare("ass ta ta ta", "ass ta ta ta")

