import json
from pathlib import Path


# this implementation works only for org.apache.commons.*
def get_javadoc_documentation(source, javadocJsonPath, method_name):
    target_path = source.replace("\\", ".").split(".")[4::]
    target_file = ".".join(target_path).replace("java", "json")

    target_file_path = Path(javadocJsonPath).joinpath(target_file)

    print(target_file_path)

    try:
        with open(str(target_file_path), "r") as file:
            json_data = file.read()
            json_object = json.loads(json_data)
            for method in json_object["methods"]:
                if method["name"] == method_name:
                    return method["docString"]
            return "No javadoc provided."
    except IOError:
        return "No javadoc provided."
    except:
        return "No javadoc provided."