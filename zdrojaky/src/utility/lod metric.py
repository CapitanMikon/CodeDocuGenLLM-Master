import argparse
import json
import numpy as np
from pathlib import Path

from utility.constants import ROOT_IMPROVED_GENERATED_DOC_DATA, ROOT_GENERATED_DOC_DATA

JAVADOC_GENER_ITERATION = 'improved_javadoc'  # 2x generovany javadoc (pri 2. generovani obohateny o kontext)
# JAVADOC_GENER_ITERATION = 'javadoc' # 1x generovany javadoc
# custom_dir = Path("..", ROOT_IMPROVED_GENERATED_DOC_DATA, "commons-text-master-docbyai")


def reformat(text):
    t = text.replace("/**", "")
    t = t.replace("*/", "")
    lines = t.split("\n")

    for i in range(len(lines)):
        lines[i] = lines[i].strip()
        lines[i] = lines[i].replace("@param", "")
        lines[i] = lines[i].replace("@throws", "")
        lines[i] = lines[i].replace("@return", "")
        if lines[i].startswith("*"):
            lines[i] = lines[i][1:]

        lines[i] = lines[i].strip()
        if len(lines[i]) > 0 and not lines[i].endswith("."):
            lines[i] += '.'

    return "\n".join(lines)


def calculate_sentences(javadoc):
    edited = reformat(javadoc)
    l = [x.strip() for x in edited.split(".")]

    total = 0
    for e in l:
        if len(e) > 0:
            total += 1

    return total


def process_entry(javadoc_by_ai):
    assert JAVADOC_GENER_ITERATION in javadoc_by_ai
    lod_score = calculate_sentences(javadoc_by_ai[JAVADOC_GENER_ITERATION])
    return lod_score


def run_calculate_lod(input_ai_dir):
    json_file_paths_ai = Path(input_ai_dir).glob("*.json")
    lod = []

    for path in json_file_paths_ai:
        with open(str(path), "r") as f:
            ai_javadoc_data = json.loads(f.read())

        assert len(ai_javadoc_data) > 0

        for entry in ai_javadoc_data:
            lod_count = process_entry(entry)
            lod.append(lod_count)

    return lod


def save_data(data, filename):
    with open(f"{filename}.json", "w") as output_file:
        output_file.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='evaluate', description="")
    parser.add_argument('--dir', help="dir for extracted ai (improved/normal) javadoc data", required=True)
    # parser.add_argument('--filename', help="output file name, without extension", required=True)
    args = parser.parse_args()

    data = run_calculate_lod(args.dir)

    print(f"Total: {np.sum(data)}")
    print(f"Avg: {np.average(data)}")
    print(f"Mean: {np.mean(data)}")
    print(f"Min: {np.min(data)}")
    print(f"Max: {np.max(data)}")
