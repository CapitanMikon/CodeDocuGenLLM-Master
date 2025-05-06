import tree_sitter_javascript as ts_javascript
from tree_sitter import Language, Parser

from codeparsers import CodeParser


class JavaScriptCodeParser(CodeParser):

    def __init__(self, repo_name):
        CodeParser.__init__(self, repo_name)
        self.__file_content = None
        self.__ast_tree = None
        self.__methods = None
        self.__source_path = None
        self.__called_methods = None

    def parse(self, java_source_path):
        self.__source_path = java_source_path

        parser = Parser(Language(ts_javascript.language()))

        with open(self.__source_path, 'r', encoding="utf-8") as r:
            self.__file_content = r.read()

        self.__ast_tree = parser.parse(self.__file_content.encode("utf8"), encoding="utf8")

        self.__methods = {}
        self.__called_methods = {}

        self.__traverse_tree()
        self.extracted_method_counter += len(self.__methods)
        print(f"\tExtracted {len(self.__methods)} methods from {self._get_relative_repo_path(self.__source_path)}")

    def get_parsed_data_json(self):
        return self.__data_to_json()

    def __extract_called_methods(self, method_node):
        cursor = method_node.walk()
        visited_children = False
        called_methods = []
        while True:
            if not visited_children:
                if cursor.node.type == "call_expression":
                    called_method_name = self.__get_method_node_name(cursor.node.text.decode("utf8"))
                    if not called_methods.__contains__(called_method_name):
                        called_methods.append(called_method_name)
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break
        return called_methods

    def __get_method_node_name(self, snippet):
        method_name = ""
        for c in snippet:
            if c == '(':
                break
            method_name += c
        return method_name.strip()

    def __traverse_tree(self):
        cursor = self.__ast_tree.walk()

        visited_children = False
        while True:
            if not visited_children:
                # if cursor.node.type == "identifier":
                if cursor.node.type == "function_declaration":
                    method_text = cursor.node.text.decode("utf8")
                    signature = self.__get_signature_from_snippet(method_text)
                    if cursor.node.prev_sibling.type == "export":
                        signature = "export " + signature
                    method_name = self.__get_name_from_signature(signature)
                    called_methods = self.__extract_called_methods(cursor.node)

                    self.__methods[method_name] = method_text
                    self.__called_methods[method_name] = called_methods
                elif cursor.node.type == "export_statement":
                    method_text = cursor.node.text.decode("utf8")
                    signature = self.__get_signature_from_snippet(method_text)
                    method_name = self.__get_name_from_signature(signature)
                    called_methods = self.__extract_called_methods(cursor.node)

                    self.__methods[method_name] = method_text
                    self.__called_methods[method_name] = called_methods
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif not cursor.goto_parent():
                break

    def __get_node_text(self, node):
        return self.__file_content[node.start_byte:node.end_byte]

    def __get_signature_from_snippet(self, snippet):
        signature = ""
        for body in snippet:
            if body == '{':
                break
            signature += body
        return signature.strip()

    def __get_name_from_signature(self, signature):
        name = ""
        index = 0
        for c in signature:
            if c == '(':
                break
            index += 1

        index -= 1

        while index > 0:
            # special case where method does not have name
            if name == "function":
                break
            if signature[index] == " ":
                break
            name = signature[index] + name
            index -= 1

        return name.strip()

    def __data_to_json(self):
        json_data = []
        for key, value in self.__methods.items():
            data_item = {"signature": self.__get_signature_from_snippet(value),
                         "implementation": value,
                         "called_methods": self.__called_methods[key],
                         "repository": self._repo_name,
                         "source": self._get_relative_repo_path(self.__source_path)
                         }
            json_data.append(data_item)
        return json_data

# Parser limitations
#   - whole file is loaded => no large files
#   - add more if any
