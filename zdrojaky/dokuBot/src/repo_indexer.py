import sys
from json import dumps as json_dumps
from os import makedirs as mkdir
from pathlib import Path
from shutil import rmtree
import argparse

from Exceptions import ExtNotSupported
from codeparsers import CodeParser, JavaCodeParser, JavaScriptCodeParser

from utility.constants import ROOT_INDEXED_REPO_DATA


def save_to_disk(json, repo_name, file_name):
    mkdir(ROOT_INDEXED_REPO_DATA, exist_ok=True)
    mkdir(f"{ROOT_INDEXED_REPO_DATA}\\{repo_name}", exist_ok=True)

    destination = Path(f"{ROOT_INDEXED_REPO_DATA}\\{repo_name}\\{file_name}_1.json")

    number = 1
    while Path.exists(destination):
        number += 1
        destination = Path(f"{ROOT_INDEXED_REPO_DATA}\\{repo_name}\\{file_name}_{number}.json")

    with open(str(destination), "w") as file:
        file.write(json)


def remove_existing_data(repo_name):
    to_remove = Path(f"{ROOT_INDEXED_REPO_DATA}\\{repo_name}")

    if to_remove.is_dir():
        rmtree(to_remove)

    print(f"Removed data from {ROOT_INDEXED_REPO_DATA}\\{repo_name}.")


def get_parser(ext, repository_name):
    if ext == ".java":
        return JavaCodeParser(repository_name)
    elif ext == ".js":
        return JavaScriptCodeParser(repository_name)
    else:
        raise ExtNotSupported(ext)


def index_repo_files_with_ext(directory, ext):
    repository_name = Path(directory).stem

    remove_existing_data(repository_name)

    repo_file_paths_with_ext = Path(directory).rglob(f"*{ext}")
    #possible problem when saving path in (source) in windows and unix \\ vs //

    total_processed_methods = 0

    for path in repo_file_paths_with_ext:
        print(f"Processing: {path}")
        parser: CodeParser = get_parser(ext, repository_name)
        parser.parse(str(path))

        total_processed_methods += parser.extracted_method_counter

        parsed_data = parser.get_parsed_data_json()

        if len(parsed_data) > 0:
            save_to_disk(json_dumps(parsed_data, indent=4), parsed_data[0].get("repository"), path.stem)
        else:
            total_processed_methods -= parser.extracted_method_counter
            print(f"\tNo methods were extracted after filtering")

        # print(json_dumps(parsed_data, indent=4))
    print(f"Total processed methods while indexing repo: {total_processed_methods}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='RepoIndexer',
                                     description="index files with selected extension in provided repository")
    parser.add_argument('--dir', help='directory of repository that will be parsed with %(prog)', required=True)
    parser.add_argument('--ext', help='file extensions of language (supported: java, js)', required='--dir' in sys.argv)
    args = parser.parse_args()

    index_repo_files_with_ext(args.dir, "." + args.ext)
    # index_repo_files_with_ext(DIRECTORY, ".js")
    """
    Repo Name restrictions: (for now, since it is used as collection name in chromaDB :))
    (1) contains 3-63 characters 
    (2) starts and ends with an alphanumeric character 
    (3) otherwise contains only alphanumeric characters, underscores or hyphens (-) 
    (4) contains no two consecutive periods (..) 
    (5) is not a valid IPv4 address 
    """




