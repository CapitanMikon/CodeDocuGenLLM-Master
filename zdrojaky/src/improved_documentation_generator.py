# langsmith integration
# from dotenv import load_dotenv
# load_dotenv()

from utility.improved_doc_helper import get_dependent_methods_data
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

import json
import re
from pathlib import Path
from utility.utils import get_language_by_ext
from os import makedirs as mkdir
from shutil import rmtree
import argparse
from sys import stderr as STDERR

from utility.constants import ROOT_IMPROVED_GENERATED_DOC_DATA
from utility.Logger import Logger

prompt_templateA = """
You are senior {LANGUAGE} programmer. Write documentation comments for the Javadoc. If present in given method include @params, @return, @throws javadoc tags. 

Here are some methods that are called within the method for better documentation:
{DEPENDENCY}

Generate more accurate javadoc comment only for this one method and output only the javadoc comment:
{METHOD}
"""

prompt_templateB = """
You are senior {LANGUAGE} programmer. Write documentation comments for the Javadoc. If present in given method include @params, @return, @throws javadoc tags. 

Generate more accurate javadoc comment only for this one method and output only the javadoc comment:
{METHOD}
"""
logger = Logger(Path(__file__).name)

def create_simple_documentation_generation_chainA():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("user", prompt_templateA),
        ]
    )

    llm = ChatOllama(
        model="llama3.1:8b-instruct-q4_K_M",
        temperature=0,
        base_url="http://192.168.0.138:11434",
        num_ctx=(8092 + 2048)
    )

    chain = prompt | llm
    return chain


def create_simple_documentation_generation_chainB():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("user", prompt_templateB),
        ]
    )

    llm = ChatOllama(
        model="llama3.1:8b-instruct-q4_K_M",
        temperature=0,
        base_url="http://192.168.0.138:11434",
        num_ctx=(8092 + 2048)
    )

    chain = prompt | llm
    return chain


def save_to_disk(json, repo_name, file_name):
    mkdir(ROOT_IMPROVED_GENERATED_DOC_DATA, exist_ok=True)
    mkdir(f"{ROOT_IMPROVED_GENERATED_DOC_DATA}\\{repo_name}", exist_ok=True)
    destination = Path(f"{ROOT_IMPROVED_GENERATED_DOC_DATA}\\{repo_name}\\{file_name}.json")

    with open(str(destination), "w") as file:
        file.write(json)


def remove_existing_data(repo):
    to_remove = Path(ROOT_IMPROVED_GENERATED_DOC_DATA, repo)

    if to_remove.is_dir():
        rmtree(to_remove)

    print(f"Removed data from {to_remove}.")


def contains_subdirectory(directory):
    path_object = Path(directory)
    for item in path_object.iterdir():
        if item.is_dir():
            return True
    return False


def process_json_file_with_path(path, repo):

    # existing_path = Path(f"{ROOT_IMPROVED_GENERATED_DOC_DATA}\\{repo}\\{Path(path).stem}.json")
    # if existing_path.exists():
    #     print(
    #         f"\n #####SKIPPING####### \n \t{path}")
    #     return

    with open(path, 'r') as file:
        json_text = file.read()

    json_object = json.loads(json_text)
    output_data = []

    for obj in json_object:
        language = get_language_by_ext(Path(obj["source"]).suffix)
        improved_generated_documentation = "STUB"
        pattern = r'/\*\*(.*?)\*/'

        dependency = get_dependent_methods_data(obj['called_methods'], obj['repository'], Path(obj['source']).stem)
        chainA = create_simple_documentation_generation_chainA()
        chainB = create_simple_documentation_generation_chainB()

        chain = chainA if dependency != "" else chainB
        print(
            f"\n ####### \n \tSignature: {obj['signature']} Lang: {language} Dependency? {'yes' if dependency != '' else 'no'}")

        javadoc_with_method = obj['javadoc'] + obj['implementation'] if obj['javadoc'] != "INVALID FORMAT" else "" + obj['implementation']

        response = chain.invoke({"LANGUAGE": language, "METHOD": javadoc_with_method, "DEPENDENCY": dependency})
        logger.log_run(response, chain)
        matches = re.findall(pattern, response.content, re.DOTALL)

        try:
            improved_generated_documentation = "/**" + matches[0] + "*/\n"
        except IndexError:
            print(f"#### ERROR: \tSignature: {obj['signature']}")
            improved_generated_documentation = "INVALID FORMAT"
        print(response.content)

        obj["improved_javadoc"] = improved_generated_documentation
        output_data.append(obj)

    output_json = json.dumps(output_data, indent=4)
    save_to_disk(output_json, repo, Path(path).stem)


def generate_doc(data_path):
    json_files_path = Path(data_path)

    if contains_subdirectory(json_files_path):
        print("Given directory should not contain subfolders!", file=STDERR)
        exit(-1)

    repo = json_files_path.stem
    json_file_paths = json_files_path.glob("*.json")

    for path in json_file_paths:
        print(f"Processing: {path}")
        process_json_file_with_path(str(path), repo)
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='DocGen',
                                     description="")
    parser.add_argument('--dir',
                        help="Directory of data that will be given to AI model to generate doc. Given directory should not contain any subdirectories.",
                        required=True)
    args = parser.parse_args()

    logger.start_logging()
    generate_doc(args.dir)
    logger.end_logging()
