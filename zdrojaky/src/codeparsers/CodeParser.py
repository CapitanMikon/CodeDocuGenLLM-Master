from pathlib import Path


class CodeParser:

    def __init__(self, repo_name):
        self._repo_name = repo_name
        self.extracted_method_counter = 0

    def parse(self, file):
        pass

    def get_parsed_data_json(self):
        pass

    def _get_relative_repo_path(self, path):
        p = Path(path).parts
        index = p.index(self._repo_name)

        relative_path = Path()
        relative_repo_path_list = p[index:]

        for sub_path in relative_repo_path_list:
            relative_path = Path.joinpath(relative_path, sub_path)

        return str(relative_path)
