import json
from typing import Dict

def load_json_file(file_path: str) -> Dict:
    """
    读取JSON文件。
    """

    with open(file_path, 'r', encoding='utf-8') as file:
        json_data = file.read()
    return json.loads(json_data)
