import json
from pathlib import Path

from utility.constants import ROOT_GENERATED_DOC_DATA


def get_dependent_methods_data(list_of_called_methods, repo_name, source_file):
    dependent_method_data_list = []

    # open only json file of same class, find method with name from filtered and append to list
    repo_path = Path(ROOT_GENERATED_DOC_DATA, repo_name)
    json_file_paths = repo_path.glob("*.json")

    for path in json_file_paths:
        if source_file in path.stem:
            continue

        # print(f"SRC:{source_file}. \nGetting methods from {path}")

        with open(str(path), 'r') as file:
            json_object = json.loads(file.read())

        for obj in json_object:
            for m in list_of_called_methods:
                if m == obj['name']:
                    dependent_method_data_list.append(
                        {
                            "code": obj['implementation'],
                            "javadoc": obj['javadoc'] if obj['javadoc'] != "INVALID FORMAT" else ""
                        }
                    )

    # TODO: limit max dependency list size. Problem 22k > tokens of context
    max_dependency_size = 5
    if len(dependent_method_data_list) > max_dependency_size:
        dependent_method_data_list = dependent_method_data_list[:max_dependency_size]

    result = ""
    for d in dependent_method_data_list:
        result += f"{d.get('javadoc')}\n{d.get('code')}\n"

    return result
