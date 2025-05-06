import javalang
from codeparsers import CodeParser


class JavaCodeParser(CodeParser):

    def __init__(self, repo_name):
        CodeParser.__init__(self, repo_name)
        self.__file_content = None
        self.__file_lines = None
        self.__ast_tree = None
        self.__methods = None
        self.__javadocs = None
        self.__source_path = None
        self.__called_methods = None

    def parse(self, java_source_path):
        self.__source_path = java_source_path

        with open(self.__source_path, 'r', encoding="utf-8") as r:
            self.__file_lines = r.readlines()
            self.__file_content = ''.join(self.__file_lines)

        lex = None
        self.__ast_tree = javalang.parse.parse(self.__file_content)
        self.__methods = {}
        self.__javadocs = {}

        for _, method_node in self.__ast_tree.filter(javalang.tree.MethodDeclaration):
            if "abstract" in method_node.modifiers or method_node.name == "toString":
                continue

            startpos, endpos, startline, endline = self.__get_method_start_and_end(method_node)
            method_text, startline, endline, lex = self.__get_method_text(startpos, endpos, startline, endline, lex)
            javadoc_text = method_node.documentation if method_node.documentation is not None else ""
            self.__javadocs[method_node.name] = javadoc_text
            self.__extract_called_methods(method_node)
            self.__methods[method_node.name] = method_text

        self.extracted_method_counter += len(self.__methods)
        print(f"\tExtracted {len(self.__methods)} methods from {self._get_relative_repo_path(self.__source_path)}")

    def get_parsed_data_json(self):
        return self.__data_to_json()

    def __extract_called_methods(self, method_node):
        if not self.__called_methods:
            self.__called_methods = {}

        for method_invocation_node in method_node.filter(javalang.tree.MethodInvocation):
            called_method_name = method_invocation_node[1].member
            if method_node.name not in self.__called_methods:
                self.__called_methods[method_node.name] = []
                self.__called_methods[method_node.name].append(called_method_name)
            else:
                if not self.__called_methods[method_node.name].__contains__(called_method_name):
                    self.__called_methods[method_node.name].append(called_method_name)

    def __get_method_start_and_end(self, method_node):
        startpos, endpos, startline, endline = None, None, None, None

        for path, node in self.__ast_tree:
            if startpos is not None and method_node not in path:
                endpos = node.position
                endline = node.position.line if node.position is not None else None
                break
            if startpos is None and node == method_node:
                startpos = node.position
                startline = node.position.line if node.position is not None else None
        return startpos, endpos, startline, endline

    def __get_method_text(self, startpos, endpos, startline, endline, last_endline_index):
        if startpos is None:
            return "", None, None, None
        else:
            startline_index = startline - 1
            endline_index = endline - 1 if endpos is not None else None

            meth_text = "<ST>".join(self.__file_lines[startline_index:endline_index])
            meth_text = meth_text[:meth_text.rfind("}") + 1]

            if not abs(meth_text.count("}") - meth_text.count("{")) == 0:
                brace_diff = abs(meth_text.count("}") - meth_text.count("{"))
                for _ in range(brace_diff):
                    meth_text = meth_text[:meth_text.rfind("}")]
                    meth_text = meth_text[:meth_text.rfind("}") + 1]

            meth_lines = meth_text.split("<ST>")

            for i in range(0, len(meth_lines)):
                if '{' in meth_lines[i]:
                    body_start = i
                    break

            #
            if len(meth_lines) > 1 and meth_lines[0] != "":
                brace_count = 0
                for j in range(body_start, len(meth_lines)):
                    brace_count += meth_lines[j].count('{')
                    brace_count -= meth_lines[j].count('}')
                    if brace_count == 0:
                        body_end = j
                        break
                meth_text = "".join(meth_lines[:body_end+1])  # excluding outer braces
            else:
                meth_text = "".join(meth_lines)

            last_endline_index = startline_index + (len(meth_lines) - 1)

            return meth_text, (startline_index + 1), (last_endline_index + 1), last_endline_index

    def __get_signature_from_snippet(self, key):
        signature = ""
        wait_for_nl = False

        for body in self.__methods[key]:
            if body == '@':
                wait_for_nl = True
                signature = ''
                continue

            if wait_for_nl:
                if body != '\n':
                    continue
                wait_for_nl = False

            if body == '{':
                break
            signature += body
        return signature.strip()

    def __get_source_repo(self, path):
        split_path = path.split("\\")
        return f"{split_path[-2]}\\{split_path[-1]}"

    def __data_to_json(self):
        json_data = []
        for key, value in self.__methods.items():
            if value == "":
                continue

            data_item = {"signature": self.__get_signature_from_snippet(key),
                         "implementation": value.strip(),
                         "called_methods": self.__called_methods[key] if self.__called_methods.__contains__(key) else "",
                         "repository": self._repo_name,
                         "source": self._get_relative_repo_path(self.__source_path),
                         "name": key,
                         "javadoc": self.__javadocs[key]
                         }
            json_data.append(data_item)
        return json_data

# Parser limitations
#   - whole file is loaded => no large files
#   - add more if any
