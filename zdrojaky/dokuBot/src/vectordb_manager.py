import argparse
import json
import chromadb
import sys
from pathlib import Path

from langchain.docstore.document import Document
from langchain_chroma import Chroma

from utility.constants import CHROMA_DB_ABSOLUTE_PATH
from utility.utils import get_embedding_function


class VectorDbManager:

    def __init__(self):
        self.__db = None
        self.__collection_name = None

    def __initialize_db_connection(self):
        self.__db = Chroma(
            collection_name=self.__collection_name,
            embedding_function=get_embedding_function(),
            persist_directory=CHROMA_DB_ABSOLUTE_PATH
        )
        print(f"Initialized vector DB connection with collection {self.__collection_name}.")

    def change_db_collection(self, to_collection):
        self.__collection_name = to_collection
        self.__initialize_db_connection()

    def connect(self, collection):
        self.change_db_collection(collection)

    def __add_documents_to_db(self, docs: list[Document]):
        for document in docs:
            source = document.metadata.get("source")
            signature = document.metadata.get("signature")

            doc_key = f"{source}#{signature}"
            # print(f"DocID: {doc_id}\n")
            if len(self.__db.get(ids=[doc_key]).get("ids")) > 0:
                print(f"Updating entry with Key: {doc_key} to collection: {self.__get_collection_name()}")
            else:
                print(f"Adding entry with Key: {doc_key} to collection: {self.__get_collection_name()}")

            self.__db.add_documents([document], ids=[doc_key])

    def __get_collection_name(self):
        return self.__collection_name if self.__collection_name else 'Not specified'

    def remove_document(self, key: str):
        self.__db.delete(ids=key)
        print(f"Deleting entry from vector DB with Key: {key} from collection: {self.__get_collection_name()}")

    def add_documents_from_json_path(self, json_file_path):
        print(f"Creating documents from {json_file_path}")
        with open(json_file_path, 'r') as file:
            json_text = file.read()

        json_object = json.loads(json_text)

        for obj in json_object:
            self.add_documents_from_json_entry(obj)

    def add_documents_from_json_entry(self, json_entry):
        content = f"Documentation of {json_entry['signature']} in file {Path(json_entry['source']).name}:\n{json_entry['improved_javadoc']}"
        doc = Document(
            page_content=content,
            metadata={
                "signature": json_entry['signature'],
                "source": json_entry['source'],
                "code": json_entry['implementation'],
                "called_methods": ", ".join(json_entry['called_methods']),  # must be string
            })
        self.__add_documents_to_db([doc])

    def print_items_from_vector_db(self):
        db_items = self.__db.get(include=[])
        # print(f"Total documents in DB: {len(db_items.get('ids'))}\nKeys: {db_items.get('ids')}")
        print(f"Total entries in vector DB collection {self.__get_collection_name()}: {len(db_items.get('ids'))}")
        for item in db_items.get('ids'):
            print(self.__db.get(item))

    def get_all_methods_in_collection(self):
        db_items = self.__db.get(include=[])
        print(f"Total entries in vector DB collection {self.__get_collection_name()}: {len(db_items.get('ids'))}")
        methods = []
        for item in db_items.get('ids'):
            methods.append(item.split("#")[1])
        return methods


def list_collection_items(collection):
    client = chromadb.PersistentClient(path=CHROMA_DB_ABSOLUTE_PATH)
    collections = get_collections_from_chromadb(client)

    if not collections.__contains__(collection):
        print(f"Unable to list items from collection \"{collection}\". Collection with such name does not exist.")
        exit(0)

    db_manager = VectorDbManager()
    db_manager.connect(collection)
    db_manager.print_items_from_vector_db()


def delete_collection(collection_name):
    client = chromadb.PersistentClient(path=CHROMA_DB_ABSOLUTE_PATH)
    collections = get_collections_from_chromadb(client)

    if not collections.__contains__(collection_name):
        print(f"Unable to delete collection \"{collection_name}\". Collection with such name does not exist.")
        exit(0)

    print(f"Successfully deleted collection \"{collection_name}\".")
    client.delete_collection(collection_name)


def get_collections_from_chromadb(client=None) -> list:
    collections = []
    if client:
        for collection in client.list_collections():
            collections.append(collection.name)
    else:
        for collection in chromadb.PersistentClient(path=CHROMA_DB_ABSOLUTE_PATH).list_collections():
            collections.append(collection.name)
    return collections


def list_collections():
    print(get_collections_from_chromadb())


def process_json_file(path):
    with open(path, 'r') as file:
        json_text = file.read()

    json_object = json.loads(json_text)
    output_data = []
    methods_in_cur_json_count = 0

    db_manager = VectorDbManager()

    for obj in json_object:
        methods_in_cur_json_count += 1
        collection = obj["repository"]
        db_manager.connect(collection)
        db_manager.add_documents_from_json_entry(obj)

    return methods_in_cur_json_count


def add_documents_from_folder(folder):
    json_files_path = Path(folder)

    json_file_paths = json_files_path.rglob("*.json")

    total_processed_methods = 0

    for path in json_file_paths:
        print(f"Processing: {path}")
        processed_count = process_json_file(str(path))
        total_processed_methods += processed_count

    print(f"Total added entries: {total_processed_methods}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='vectordb_manager',
                                     description="tool for managing vector db")
    exclusive_parser = parser.add_mutually_exclusive_group()

    exclusive_parser.add_argument('-a', '--add',
                                  help='add <path> \ndirectory of json files to be added to vector db. It can be root '
                                       'directory with all jsons in subdirectories', type=str)
    exclusive_parser.add_argument('--list_collections', help='list collections in current vector db',
                                  action='store_true')
    exclusive_parser.add_argument('--delete_collection', help='delete_collection <collection_name> \ndelete collection from current vector db')
    exclusive_parser.add_argument('--list_items', help='list_items <collection_name> \ndelete collection from current vector db')
    args = parser.parse_args()

    if args.add:
        add_documents_from_folder(args.add)
    elif args.list_collections:
        list_collections()
    elif args.delete_collection:
        delete_collection(args.delete_collection)
    elif args.list_items:
        list_collection_items(args.list_items)
    else:
        parser.print_help()

    # print(vars(args))
