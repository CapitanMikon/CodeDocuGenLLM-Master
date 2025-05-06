import argparse
import json
import sys

from nltk.translate import bleu_score
from nltk.translate.bleu_score import corpus_bleu


"""
    Process entry. Compare AI texts to human texts.
    Returns dict with properties:
        1. all None values if ai javadoc is INVALID FORMAT
        2. has empty lists of params/throws if not same in ai javadoc
        3. decs and ret is None if human javadoc desc is empty string
"""
def process_entry(javadoc_by_human, javadoc_by_ai):
    bleu_score_description = calculate_bleu_score(javadoc_by_human['description'], javadoc_by_ai['description'])
    bleu_score_return = calculate_bleu_score(javadoc_by_human['return'], javadoc_by_ai['return'])
    bleu_score_params = []
    bleu_score_throws = []

    if javadoc_by_ai['description'] == "INVALID FORMAT":
        bleu_score_description = None
        bleu_score_return = None
        bleu_score_params = None
        bleu_score_throws = None
        return {"signature": javadoc_by_human['signature'], "bleu_desc": bleu_score_description, "bleu_params": bleu_score_params, "bleu_return_desc": bleu_score_return, "bleu_throws": bleu_score_throws}

    # TODO: loop through param names and find them in ai or return default
    # assumes all params are in order as in human
    if len(javadoc_by_human['params']) == len(javadoc_by_ai['params']):
        for i in range(len(javadoc_by_human['params'])):
            param_bleu_score = calculate_bleu_score(javadoc_by_human['params'][i]['param_desc'], javadoc_by_ai['params'][i]['param_desc'])
            bleu_score_params.append(param_bleu_score)
    else:
        print(f"{javadoc_by_human['signature']}: \n\tlen(javadoc_by_human['params']) != len(javadoc_by_ai['params'])", file=sys.stderr, flush=True)

    # assumes all params are in order as in human
    if len(javadoc_by_human['throws']) == len(javadoc_by_ai['throws']):
        for i in range(len(javadoc_by_human['throws'])):
            throws_bleu_score = calculate_bleu_score(javadoc_by_human['throws'][i]['thrown_excep_desc'], javadoc_by_ai['throws'][i]['thrown_excep_desc'])
            bleu_score_throws.append(throws_bleu_score)
    else:
        print(f"{javadoc_by_human['signature']}: \n\tlen(javadoc_by_human['throws']) != len(javadoc_by_ai['throws'])", file=sys.stderr, flush=True)

    return {"signature": javadoc_by_human['signature'], "bleu_desc": bleu_score_description, "bleu_params": bleu_score_params, "bleu_return_desc": bleu_score_return, "bleu_throws": bleu_score_throws}


"""return bleu score or None if human_text is empty string."""
def calculate_bleu_score(human_text, ai_text):

    corpus_bleu_score_data = {
        "bleu": 0,
        "bleu-1": 0,
        "bleu-2": 0,
        "bleu-3": 0,
        "bleu-4": 0,
        "smoothing_func": "none",
    }

    if ai_text == "":
        print("Ai text empty", file=sys.stderr, flush=True)
        return corpus_bleu_score_data
    if human_text == "":
        print("Human text empty", file=sys.stderr, flush=True)
        return None

    reference = [[human_text.split()]]
    ai_generated = [ai_text.split()]

    fn = bleu_score.SmoothingFunction().method1
    corpus_bleu_score = corpus_bleu(reference, ai_generated, smoothing_function=fn)
    bleu_1 = corpus_bleu(reference, ai_generated, weights=(1, 0, 0, 0), smoothing_function=fn)
    bleu_2 = corpus_bleu(reference, ai_generated, weights=(0, 1, 0, 0), smoothing_function=fn)
    bleu_3 = corpus_bleu(reference, ai_generated, weights=(0, 0, 1, 0), smoothing_function=fn)
    bleu_4 = corpus_bleu(reference, ai_generated, weights=(0, 0, 0, 1), smoothing_function=fn)

    corpus_bleu_score_data["bleu"] = corpus_bleu_score
    corpus_bleu_score_data["bleu-1"] = bleu_1
    corpus_bleu_score_data["bleu-2"] = bleu_2
    corpus_bleu_score_data["bleu-3"] = bleu_3
    corpus_bleu_score_data["bleu-4"] = bleu_4
    corpus_bleu_score_data["smoothing_func"] = "method1"

    return corpus_bleu_score_data


def run_compare_bleu_score(input_human_dir, input_ai_dir):

    bleu_scores_data = []

    with open(input_human_dir, "r") as f:
        human_javadoc_data = json.loads(f.read())

    with open(input_ai_dir, "r") as f:
        ai_javadoc_data = json.loads(f.read())

    if len(human_javadoc_data) != len(ai_javadoc_data):
        raise Exception("len != len")

    for i in range(len(human_javadoc_data)):

        assert human_javadoc_data[i]['signature'] == ai_javadoc_data[i]['signature']

        e = process_entry(human_javadoc_data[i], ai_javadoc_data[i])
        bleu_scores_data.append(e)

    return bleu_scores_data


def save_data(data, filename):
    with open(f"{filename}.json", "w") as output_file:
        output_file.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='evaluate', description="")
    parser.add_argument('--human', help="dir for extracted human javadoc data", required=True)
    parser.add_argument('--ai', help="dir for extracted ai (improved/normal) javadoc data", required=True)
    parser.add_argument('--filename', help="output file name, without extension", required=True)
    args = parser.parse_args()

    data = run_compare_bleu_score(args.human, args.ai)
    save_data(data, args.filename)
