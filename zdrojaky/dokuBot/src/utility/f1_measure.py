import argparse
import json
from pathlib import Path

from utility.data_extractor import extract_data_from_json_entry

JAVADOC_GENER_ITERATION = 'improved_javadoc'  # 2x generovany javadoc (pri 2. generovani obohateny o kontext)
# JAVADOC_GENER_ITERATION = 'javadoc' # 1x generovany javadoc


def get_method_params_count(signature):
    total_params = 0

    start_index = signature.find('(')
    assert start_index > -1

    param_string = signature[start_index:]
    if len(param_string) == 2:  # method():
        return 0

    if param_string.count(',') == 0:  # method(param)
        return 1

    total_params = param_string.count(',') + 1

    return total_params


# predpokladame ze ked ma v params nieco tak to ma nazvy parametrov take ake su v signature :)
def f1_measure(method_data):
    true_positive = 0  # je to v kode (ma to tam byt) a llm to dal do javadoc
    false_positive = 0  # nie je to v kode (nema to tam byt) ale llm to dal do javadoc
    true_negative = 0  # nie je to v kode (nema to tam byt) a aj llm to nedal do javadoc
    false_negative = 0  # je to v kode (ma to tam byt) ale llm to nedal do javadoc

    extracted_javadoc_data = extract_data_from_json_entry(method_data[JAVADOC_GENER_ITERATION],
                                                          method_data['signature'])

    # 1. check description
    if extracted_javadoc_data['description'] != "":  # ma mat popis a llm dal popis
        true_positive += 1
    elif extracted_javadoc_data['description'] == "":  # ma mat popis a llm nedal popis
        false_negative += 1

    # 2. check params
    method_real_number_of_params = get_method_params_count(method_data['signature'])

    if method_real_number_of_params > 0:
        if extracted_javadoc_data['params'] != "":  # ma params a llm pridal params
            if method_real_number_of_params == len(
                    extracted_javadoc_data['params']):  # ma params a llm pridal params presne rovnaky pocet
                true_positive += method_real_number_of_params
            elif method_real_number_of_params > len(
                    extracted_javadoc_data['params']):  # ma params a llm pridal params mensi pocet
                true_positive += len(extracted_javadoc_data['params'])
                false_negative += abs(
                    method_real_number_of_params - len(extracted_javadoc_data['params']))  # ma params a llm nepridal
            else:  # ma params a llm pridal params vacsi pocet
                true_positive += method_real_number_of_params
                false_positive += abs(len(extracted_javadoc_data[
                                              'params']) - method_real_number_of_params)  # ma params a llm pridal navyse, cize original nema ale llm pridal
        elif extracted_javadoc_data['params'] == "":  # nema params a llm nepridal params
            false_negative += method_real_number_of_params
    else:
        if extracted_javadoc_data['params'] != "":  # nema params a llm mysli ze ma
            false_positive += len(extracted_javadoc_data['params'])
        elif extracted_javadoc_data['params'] == "":  # nema params a llm nepridal params
            true_negative += 1

    # 3. check return
    total_returns = method_data['implementation'].count("return")
    if total_returns > 0:
        if extracted_javadoc_data['return'] != "":  # ma return value a llm pridal return desc
            true_positive += 1
        elif extracted_javadoc_data['return'] == "":  # ma return value a llm nepridal return desc
            false_negative += 1
    else:
        if extracted_javadoc_data['return'] != "":  # nema return value a llm mysli ze ma return
            false_positive += 1
        elif extracted_javadoc_data['return'] == "":  # nema return value a llm nepridal return desc
            true_negative += 1

    # 4. check throws
    total_throws = method_data['implementation'].count("throw new")
    if total_throws > 0:
        if extracted_javadoc_data['throws'] != "":  # ma throws a llm pridal throws
            if total_throws == len(
                    extracted_javadoc_data['throws']):  # ma throws a llm pridal throws presne rovnaky pocet
                true_positive += total_throws
            elif total_throws > len(extracted_javadoc_data['throws']):  # ma throws a llm pridal throws mensi pocet
                true_positive += len(extracted_javadoc_data['throws'])
                false_negative += abs(total_throws - len(extracted_javadoc_data['throws']))  # ma throws a llm nepridal
            else:  # ma throws a llm pridal throws vacsi pocet
                true_positive += total_throws
                false_positive += abs(len(extracted_javadoc_data[
                                              'throws']) - total_throws)  # ma throws a llm pridal navyse, cize original nema ale llm pridal
        elif extracted_javadoc_data['throws'] == "":  # ma throws a llm nepridal throws
            false_negative += total_throws
    else:
        if extracted_javadoc_data['throws'] != "":  # nema throws a llm mysli ze ma
            false_positive += len(extracted_javadoc_data['throws'])
        elif extracted_javadoc_data['throws'] == "":  # nema throws a llm nepridal throws
            true_negative += 1

    return [true_positive, false_positive, true_negative, false_negative]


def process_entry(javadoc_by_ai):
    # print(javadoc_by_ai['javadoc'])
    # print(javadoc_by_ai['signature'])
    # print(javadoc_by_ai['implementation'])
    f1_score = f1_measure(javadoc_by_ai)
    # print(f1_score)
    # print("[TP, FP, TN, FN]")
    return f1_score


def run_calc_f1_scores(input_ai_dir):
    json_file_paths_ai = Path(input_ai_dir).glob("*.json")

    # [TP, FP, TN, FN]
    f1_scores = [0, 0, 0, 0]

    for path in json_file_paths_ai:
        with open(str(path), "r") as f:
            ai_javadoc_data = json.loads(f.read())

        assert len(ai_javadoc_data) > 0

        for entry in ai_javadoc_data:
            e1 = process_entry(entry)
            f1_scores[0] += e1[0]
            f1_scores[1] += e1[1]
            f1_scores[2] += e1[2]
            f1_scores[3] += e1[3]

    return f1_scores


def save_data(data, filename):
    with open(f"{filename}.json", "w") as output_file:
        output_file.write(json.dumps(data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='evaluate', description="")
    parser.add_argument('--ai', help="dir for extracted ai (improved/normal) javadoc data", required=True)
    # parser.add_argument('--filename', help="output file name, without extension", required=True)
    args = parser.parse_args()

    data = run_calc_f1_scores(args.ai)
    print("[TP, FP, TN, FN]")
    print(data)

    precision = data[0] / (data[0] + data[1])
    recall = data[0] / (data[0] + data[3])
    accuracy = (data[0] + data[2]) / (data[0] + data[1] + data[2] + data[3])
    f1 = (2 * precision * recall) / (precision + recall)

    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"Accuracy: {accuracy}")
    print(f"F1: {f1}")
    # save_data(data, args.filename)
