import argparse
import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma

from utility.constants import CHROMA_DB_ABSOLUTE_PATH, CHROMADB_COLLECTION_NAME
from utility.data_extractor import extract_data_from_json_entry
from utility.utils import get_embedding_function


def add_documents_to_db(docs: list[Document]):
    db = Chroma(
        collection_name=CHROMADB_COLLECTION_NAME,
        embedding_function=get_embedding_function(),
        persist_directory=CHROMA_DB_ABSOLUTE_PATH
    )

    for document in docs:
        source = document.metadata.get("source")
        signature = document.metadata.get("signature")

        doc_key = f"{source}#{signature}"
        # print(f"DocID: {doc_id}\n")
        if len(db.get(ids=[doc_key]).get("ids")) > 0:
            print(f"Updating entry with Key: {doc_key} in collection: {CHROMADB_COLLECTION_NAME}")
        else:
            print(f"Adding entry with Key: {doc_key} in collection: {CHROMADB_COLLECTION_NAME}")

        print(f"Doc: {document}")
        db.add_documents([document], ids=[doc_key])


def add_documents_from_json_entry(json_entry):
    method_description = extract_data_from_json_entry(json_entry['javadoc'], json_entry['signature'])['description']

    doc = Document(
        page_content=method_description,
        metadata={
            "signature": json_entry['signature'],
            "name": json_entry['name'],
            "source": json_entry['source'],
            "javadoc": json_entry['javadoc'],
            "code": json_entry['implementation'],
        })

    add_documents_to_db([doc])


def process_input_dir(input_dir):
    root_dir = Path(input_dir)

    json_file_paths = root_dir.rglob("*.json")

    for path in json_file_paths:
        with open(str(path), 'r') as file:
            json_object = json.loads(file.read())

        for entry in json_object:
            add_documents_from_json_entry(entry)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='populate vec db from json', description="populate vec db from json")
    parser.add_argument('--dir', help="", required=True)
    args = parser.parse_args()

    process_input_dir(args.dir)