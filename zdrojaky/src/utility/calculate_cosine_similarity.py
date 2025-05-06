from langchain_ollama import OllamaEmbeddings
import numpy as np
from numpy.linalg import norm
import argparse
import json
from pathlib import Path


def cosine_similarity_with_embedding_model(human, ai):
    embeddings_model = OllamaEmbeddings(
        model="nomic-embed-text",
    )

    human_vector = embeddings_model.embed_query(human)
    ai_vector = embeddings_model.embed_query(ai)

    #print(human_vector[:5])
    #print(ai_vector[:5])

    cosine_similarity = np.dot(human_vector, ai_vector) / (norm(human_vector) * norm(ai_vector))
    # print("Cosine Similarity:", cosine_similarity)
    return cosine_similarity


def reformat(text):
    t = text.replace("/**", "")
    t = t.replace("*/", "")
    lines = t.split("\n")

    for i in range(len(lines)):
        lines[i] = lines[i].strip()
        if lines[i].startswith("*"):
            lines[i] = lines[i][1:]

    return "\n".join(lines)


def process_entry(javadoc_by_human, javadoc_by_ai):
    formatted_a = reformat(javadoc_by_human)
    formatted_b = reformat(javadoc_by_ai)
    cosine_score = cosine_similarity_with_embedding_model(formatted_a, formatted_b)
    return cosine_score


def run_compare_bleu_score(input_human_dir, input_ai_dir):
    json_file_paths_human = Path(input_human_dir).glob("*.json")
    json_file_paths_ai = Path(input_ai_dir).glob("*.json")

    lista = []
    listb = []

    list_a = [x for x in json_file_paths_human if x.is_file()]
    list_b = [x for x in json_file_paths_ai if x.is_file()]

    skipped = 0
    ignored_cnt = 0
    ignored = []

    assert len(list_a) == len(list_b)

    for j in range(len(list_a)):
        with open(str(list_a[j]), "r") as f:
            human_javadoc_data = json.loads(f.read())

        with open(str(list_b[j]), "r") as f:
            ai_javadoc_data = json.loads(f.read())

        assert len(human_javadoc_data) == len(ai_javadoc_data)

        #create list of skipped
        for i in range(len(human_javadoc_data)):
            assert human_javadoc_data[i]['signature'] == ai_javadoc_data[i]['signature']

            if human_javadoc_data[i]['javadoc'] == "INVALID FORMAT" or ai_javadoc_data[i]['improved_javadoc'] == "INVALID FORMAT" \
                    or human_javadoc_data[i]['javadoc'] == "" or ai_javadoc_data[i]['javadoc'] == "INVALID FORMAT":
                skipped += 1
                ignored.append(human_javadoc_data[i]['source'] + human_javadoc_data[i]['signature'])

        #skip ignored
        for i in range(len(human_javadoc_data)):
            assert human_javadoc_data[i]['signature'] == ai_javadoc_data[i]['signature']

            if human_javadoc_data[i]['source'] + human_javadoc_data[i]['signature'] in ignored\
                    or ai_javadoc_data[i]['source'] + ai_javadoc_data[i]['signature'] in ignored:
                ignored_cnt += 1
                continue

            e1 = process_entry(human_javadoc_data[i]['javadoc'], ai_javadoc_data[i]['javadoc'])
            e2 = process_entry(human_javadoc_data[i]['javadoc'], ai_javadoc_data[i]['improved_javadoc'])
            lista.append(e1)
            listb.append(e2)

    assert skipped == ignored_cnt
    print(f"Skipped: {skipped}. Reason: javadoc is empty, or not valid. Only compare valid results")

    return [lista, listb]


def save_data(data, filename):
    with open(f"{filename}.json", "w") as output_file:
        output_file.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='evaluate', description="")
    parser.add_argument('--human', help="dir for extracted human javadoc data", required=True)
    parser.add_argument('--ai', help="dir for extracted ai (improved/normal) javadoc data", required=True)
    # parser.add_argument('--filename', help="output file name, without extension", required=True)
    args = parser.parse_args()

    data = run_compare_bleu_score(args.human, args.ai)
    avg = [np.average(data[0]), np.average(data[1])]
    mean = [np.mean(data[0]), np.mean(data[1])]

    # print(data)
    total = len(data[0])

    print("Celkovo metod: " + str(total))
    print("Avg: " + str(avg))
    print("Mean: " + str(mean))
    print("Max: [" + str(np.max(data[0])) + ", " + str(np.max(data[1])) + "]")
    print("Min: [" + str(np.min(data[0])) + ", " + str(np.min(data[1])) + "]")
    print("Pocet lepsich v 1x gen doc ako avg v 2x gen doc: " + str(sum(x > avg[1] for x in data[0])))
    print("Pocet lepsich v 2x gen doc ako avg v 1x gen doc: " + str(sum(x > avg[0] for x in data[1])))

    greater = 0
    equal = 0
    less = 0
    for i in range(len(data[0])):
        if data[1][i] > data[0][i]:
            greater += 1
        elif data[1][i] == data[0][i]:
            equal += 1
        else:
            less += 1

    print("One to one compare (cos sim scores). 1x generovana doc vs 2x generovana doc:")
    print("Greater: " + str(greater))
    print("Equal: " + str(equal))
    print("Less: " + str(less))
    print("Percentualne zlepsenie 2x gen doc oproti 1x gen doc (s equal): " + str(((greater + equal) / total) * 100))
    print("Percentualne zlepsenie 2x gen doc oproti 1x gen doc (bez equal): " + str((greater / (total - equal)) * 100))

    #for i in range(len(data[0])):
    #    print(f" [{data[0][i]}, {data[1][i]}] ")

    # save_data(data, args.filename)

