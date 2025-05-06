import argparse
import json
from pathlib import Path


def extract_params(current_cursor_pos, content):
    extract_params = []

    cursor_pos = current_cursor_pos

    desc_acc = ""
    param_name = ""
    for i in range(current_cursor_pos, len(content)):
        if content[i].startswith("@return") or content[i].startswith("@throws"):
            # cursor_pos += 1
            # add last
            if param_name != "":
                extract_params.append(
                    {
                        "param_name": param_name,
                        "param_desc": desc_acc.strip(),
                    }
                )
                desc_acc = ""
                param_name = ""
            break

        #get name of param
        if content[i].startswith("@param"):
            # save previous if was found
            if param_name != "":
                extract_params.append(
                    {
                        "param_name": param_name,
                        "param_desc": desc_acc.strip(),
                    }
                )
                desc_acc = ""
                param_name = ""

            line = content[i].split(" ")
            param_name = line[1]
            desc_acc += content[i][(len(line[0]) + len(line[1]) + 1):]
            #for j in range(2, len(line)):
            #    desc_acc += line[j]
            cursor_pos += 1
            continue
        else:
            if not content[i].startswith(" "):
                desc_acc += " "

        desc_acc += content[i].strip()
        cursor_pos += 1

    #add last
    if param_name != "":
        extract_params.append(
            {
                "param_name": param_name,
                "param_desc": desc_acc.strip(),
            }
        )
    return cursor_pos, extract_params


def extract_throws(current_cursor_pos, content):
    extract_thorows = []

    cursor_pos = current_cursor_pos

    desc_acc = ""
    thrown_excep_name = ""
    for i in range(current_cursor_pos, len(content)):
        if content[i].startswith("@return") or content[i].startswith("@params"):
            # cursor_pos += 1
            # add last
            if thrown_excep_name != "":
                extract_thorows.append(
                    {
                        "thrown_excep_name": thrown_excep_name,
                        "thrown_excep_desc": desc_acc.strip(),
                    }
                )
                desc_acc = ""
                thrown_excep_name = ""
            break

        #get name of param
        if content[i].startswith("@throws"):
            # save previous if was found
            if thrown_excep_name != "":
                extract_thorows.append(
                    {
                        "thrown_excep_name": thrown_excep_name,
                        "thrown_excep_desc": desc_acc.strip(),
                    }
                )
                desc_acc = ""
                thrown_excep_name = ""

            line = content[i].split(" ")
            thrown_excep_name = line[1]
            desc_acc += content[i][(len(line[0]) + len(line[1]) + 1):]
            cursor_pos += 1
            continue
        else:
            if not content[i].startswith(" "):
                desc_acc += " "

        desc_acc += content[i].strip()
        cursor_pos += 1

    #add last
    if thrown_excep_name != "":
        extract_thorows.append(
            {
                "thrown_excep_name": thrown_excep_name,
                "thrown_excep_desc": desc_acc.strip(),
            }
        )
    return cursor_pos, extract_thorows


def extract_return(current_cursor_pos, content):
    cursor_pos = current_cursor_pos
    desc_acc = ""

    for i in range(current_cursor_pos, len(content)):
        if content[i].startswith("@throws"):
            break

        #get name of param

        if content[i].startswith("@return"):
            desc_acc += content[i][len("@return")+1:]
        else:
            if not content[i].strip().startswith(" "):
                desc_acc += " "
            desc_acc += content[i].strip()

        cursor_pos += 1

    return cursor_pos, desc_acc


def extract_data_from_json_entry(javadoc, signature):
    splited = javadoc.split("\n")

    for i in range(len(splited)):
        splited[i] = splited[i].strip()
        if len(splited[i]) == 1 or splited[i] == "/**" or splited[i] == "*/":
            splited[i] = ""
        if splited[i].startswith("* "):
            splited[i] = splited[i][2:]

    # remove empty
    temp_arr = []
    for item in splited:
        if not item == "":
            temp_arr.append(item)
    splited = temp_arr

    cursor_pos = -1
    # extract description
    desc_acc = ""
    for i in range(len(splited)):
        if splited[i].startswith("@param") or splited[i].startswith("@return") or splited[i].startswith("@throws"):
            cursor_pos += 1
            break

        if not splited[i].strip().startswith(" "):
            desc_acc += " "

        desc_acc += splited[i].strip()
        cursor_pos += 1

    desc_acc = desc_acc.strip()

    #extract params, p= None if next is not @param. -> next is @throws or @return
    extracted_javadoc_params = ""
    extracted_javadoc_return = ""
    extracted_javadoc_throws = ""

    if cursor_pos < 0:
        return {
        "signature": signature,
        "description": desc_acc,
        "params": extracted_javadoc_params,
        "throws": extracted_javadoc_throws,
        "return": extracted_javadoc_return,
    }

    if cursor_pos < len(splited):
        if splited[cursor_pos].startswith("@param"):
            p = extract_params(cursor_pos, splited)
            cursor_pos = p[0]
            extracted_javadoc_params = p[1]

    if cursor_pos < len(splited):
        if splited[cursor_pos].startswith("@return"):
            r = extract_return(cursor_pos, splited)
            cursor_pos = r[0]
            extracted_javadoc_return = r[1]

    if cursor_pos < len(splited):
        if splited[cursor_pos].startswith("@throws"):
            t = extract_throws(cursor_pos, splited)
            cursor_pos = t[0]
            extracted_javadoc_throws = t[1]

    data = {
        "signature": signature,
        "description": desc_acc,
        "params": extracted_javadoc_params,
        "throws": extracted_javadoc_throws,
        "return": extracted_javadoc_return,
    }

    return data


def extract_data(input_dir, useImprovedJavadoc, filename_prefix):
    root_dir = Path(input_dir)

    json_file_paths = root_dir.rglob("*.json")
    # print(root_dir.stem)

    # output_filename = f"{root_dir.stem}_{filename_prefix}_{datetime.datetime.now().strftime('%H-%M-%S-%d-%m-%Y')}.txt"
    output_filename = f"{root_dir.stem}_{filename_prefix}_javadoc.json"
    output_data = []

    # clear file
    with open(output_filename, "w"):
        pass

    for path in json_file_paths:
        with open(str(path), 'r') as file:
            json_object = json.loads(file.read())

        for i in range(len(json_object)):
            d = None
            if useImprovedJavadoc:
                d = extract_data_from_json_entry(json_object[i]['improved_javadoc'], json_object[i]['signature'])
            else:
                d = extract_data_from_json_entry(json_object[i]['javadoc'], json_object[i]['signature'])
            output_data.append(d)

    with open(output_filename, 'a') as output_file:
        output_file.write(json.dumps(output_data, indent=4))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='evaluate', description="")
    parser.add_argument('--dir', help="", required=True)
    parser.add_argument('--prefix', help="")
    parser.add_argument('--improved_javadoc', help="", action='store_true')
    args = parser.parse_args()

    extract_data(args.dir, args.improved_javadoc, args.prefix)

