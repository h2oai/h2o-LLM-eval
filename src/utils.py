import os
import json
from typing import List, Dict, Tuple, Union


def write_json(data: Union[Dict, List], file_name: str) -> str:
    out_file_path = os.path.abspath(file_name)
    with open(out_file_path, "w") as json_fp:
        json.dump(data, json_fp)
    return out_file_path


def read_json(json_path):
    json_data = None
    try:
        with open(json_path, "r") as json_fp:
            json_data = json.load(json_fp)
    except Exception as e:
        print(e)
    return json_data


def make_jsonl(data: List[Dict]) -> List[str]:
    return [json.dumps(row) + "\n" for row in data]


def write_jsonl(data: List[Dict], file_name: str) -> str:
    json_lines = make_jsonl(data)

    out_file_path = os.path.abspath(file_name)
    with open(out_file_path, "w") as jsonl_fp:
        jsonl_fp.writelines(json_lines)

    return out_file_path


def read_lines(file_name):
    with open(os.path.abspath(file_name), "r") as read_file:
        lines = read_file.readlines()
    return lines


def read_jsonl(file_name: str) -> Tuple[List[Dict], List[str]]:
    json_lines_raw = read_lines(file_name)
    json_lines = []
    failed_lines = []
    for l in json_lines_raw:
        try:
            json_line = json.loads(l)
        except Exception as e:
            print(e)
            failed_lines.append(l)
        else:
            json_lines.append(json_line)

    return json_lines, failed_lines