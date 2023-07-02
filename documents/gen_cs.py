import re
import json
from typing import Any, Dict

def remove_comments_and_load_json(filename: str) -> Any:
    with open(filename, "r", encoding="utf-8") as file:
        content = re.sub(r'//.*', '', file.read())
        return json.loads(content)

def get_csharp_type(obj: Any, classname: str = "") -> str:
    if isinstance(obj, bool):
        return "bool"
    elif isinstance(obj, int):
        return "int"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, str):
        return "string"
    elif isinstance(obj, list):
        if obj:  # Check if list is not empty
            return f"List<{get_csharp_type(obj[0])}>"
        else:
            return "List<object>"
    elif isinstance(obj, dict):
        attributes = "\n    ".join(f"public {get_csharp_type(v, k)} {k};" for k, v in obj.items())
        return f"[System.Serializable]\npublic class {classname.capitalize()} {{\n    {attributes}\n}}\n", classname.capitalize()
    else:
        return "object"

def generate_csharp_from_json(json_obj: Dict[str, Any], nested_classes: Dict[str, str]) -> str:
    classname = json_obj["command"].capitalize()
    attributes = "\n    ".join(f"public {nested_classes.get(k, get_csharp_type(v))} {k};" for k, v in json_obj["args"].items())
    return f"[System.Serializable]\npublic class {classname} {{\n    {attributes}\n}}\n"

def main(filename: str) -> None:
    print("""
using System.Collections.Generic;

namespace MarimoDesktopMascot
{
    namespace Messenger
    {
        public class Protocol
        {""")
    json_obj = remove_comments_and_load_json(filename)
    nested_classes = {}
    for command in json_obj:
        for k, v in command["args"].items():
            if isinstance(v, dict):
                nested_class, nested_classname = get_csharp_type(v, k.capitalize())
                print(nested_class)
                nested_classes[k] = nested_classname
    for command in json_obj:
        print(generate_csharp_from_json(command, nested_classes))
    print("""
        }
    }
}""")

if __name__ == "__main__":
    main("commands.jsonc")  # JSONCファイルの名前をここに書く
