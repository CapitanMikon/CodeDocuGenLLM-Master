# langsmith integration
from dotenv import load_dotenv

import doc_gen_helper

load_dotenv()

from langchain_ollama import ChatOllama

from langchain_core.prompts import ChatPromptTemplate

import json
import re
from pathlib import Path
from utility.utils import get_language_by_ext
from os import makedirs as mkdir, listdir
from shutil import rmtree
import argparse
from sys import stderr as STDERR

from utility.constants import ROOT_GENERATED_DOC_DATA
from utility.Logger import Logger

prompt_template ="""
You are senior {LANGUAGE} programmer. Write documentation comments for the Javadoc. If present in given method include @params, @return, @throws javadoc tags. Do not include provided method in generated documentation. Output only the documentation comments. Here is the method:

{METHOD}

Your answer:
/**
* //your javadoc comment goes here
*
*/
"""

logger = Logger(Path(__file__).name)


def create_simple_documentation_generation_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("user", prompt_template),
        ]
    )

    llm = ChatOllama(
        model="llama3.1:8b-instruct-q4_K_M",
        temperature=0,
        base_url="http://192.168.0.138:11434",
        num_ctx=8092
    )

    chain = prompt | llm
    return chain


def save_to_disk(json, repo_name, file_name):
    mkdir(ROOT_GENERATED_DOC_DATA, exist_ok=True)
    mkdir(f"{ROOT_GENERATED_DOC_DATA}\\{repo_name}", exist_ok=True)
    destination = Path(f"{ROOT_GENERATED_DOC_DATA}\\{repo_name}\\{file_name}.json")

    with open(str(destination), "w") as file:
        file.write(json)


def remove_existing_data(repo):
    to_remove = Path(ROOT_GENERATED_DOC_DATA, repo)

    if to_remove.is_dir():
        rmtree(to_remove)

    print(f"Removed data from {to_remove}.")


def contains_subdirectory(directory):
    path_object = Path(directory)
    for item in path_object.iterdir():
        if item.is_dir():
            return True
    return False


def process_json_file_with_path(path, repo, isMock, javadocJsonPath):
    chain = create_simple_documentation_generation_chain()

    with open(path, 'r') as file:
        json_text = file.read()

    json_object = json.loads(json_text)
    output_data = []

    for obj in json_object:
        language = get_language_by_ext(Path(obj["source"]).suffix)
        print(f"\tSignature: {obj['signature']} Lang: {language}")
        generated_documentation = None
        pattern = r'/\*\*(.*?)\*/'

        if isMock:
            generated_documentation = "/** \n* MOCK\n */"
        else:
            if javadocJsonPath:
                #if obj["javadoc"] == "":
                #    generated_documentation = doc_gen_helper.get_javadoc_documentation(obj["source"], javadocJsonPath, obj["name"])
                #    print("\t\tUsed doclet!")
                #else:
                generated_documentation = obj["javadoc"]
            else:
                response = chain.invoke({"LANGUAGE": language, "METHOD": obj['implementation']}) if not isMock else ""
                logger.log_run(response, chain)
                matches = re.findall(pattern, response.content, re.DOTALL)
                try:
                    generated_documentation = "/**" + matches[0] + "*/\n"
                except IndexError:
                    print("#### ERROR: \tSignature: {obj['signature']}")
                    generated_documentation = "INVALID FORMAT"
                print(response.content)

        obj["javadoc"] = generated_documentation
        # generated_documentation = "empty"
        output_data.append(obj)

    output_json = json.dumps(output_data, indent=4)
    save_to_disk(output_json, repo, Path(path).stem)


def generate_doc(data_path, isMock, javadocJsonPath):
    json_files_path = Path(data_path)

    if contains_subdirectory(json_files_path):
        print("Given directory should not contain subfolders!", file=STDERR)
        exit(-1)

    if isMock:
        print("Mock is True. Not using AI model, fill with empty string.")

    repo = json_files_path.stem
    json_file_paths = json_files_path.glob("*.json")

    remove_existing_data(repo)

    for path in json_file_paths:
        print(f"Processing: {path}")
        process_json_file_with_path(str(path), repo, isMock, javadocJsonPath)
    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='DocGen',
                                     description="")
    parser.add_argument('--dir', help="Directory of data that will be given to AI model to generate doc. Given directory should not contain any subdirectories.", required=True)
    parser.add_argument('--mock', help='skip AI generation, fill with empty string', action='store_true')
    parser.add_argument('--javadoc', help='uses documentation from javadoc, requires processed files from jsonDoclet or acquired javadoc')
    args = parser.parse_args()

    logger.start_logging()
    generate_doc(args.dir, args.mock, args.javadoc)
    logger.end_logging()
