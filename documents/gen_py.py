import re
import json
from typing import Any, List, Dict

def remove_comments_and_load_json(filename: str) -> Any:
    with open(filename, "r", encoding="utf-8") as file:
        content = re.sub(r'//.*', '', file.read())
        return json.loads(content)

def get_python_type(obj: Any, classname: str = "") -> str:
    if isinstance(obj, bool):
        return "bool"
    elif isinstance(obj, int):
        return "int"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, str):
        return "str"
    elif isinstance(obj, list):
        if obj:  # Check if list is not empty
            return f"List[{get_python_type(obj[0])}]"
        else:
            return "List[Any]"
    elif isinstance(obj, dict):
        attributes = "\n    ".join(f"{k}: {get_python_type(v, k.capitalize())}" for k, v in obj.items())
        return f"@dataclass\nclass {classname.capitalize()}:\n    {attributes}\n\n", classname.capitalize()
    else:
        return "Any"

def generate_dataclass_from_json(json_obj: Dict[str, Any], nested_classes: Dict[str, str]) -> str:
    classname = json_obj["command"].capitalize()
    args_classname = classname + "Args"
    attributes = "\n    ".join(f"{k}: {nested_classes.get(k.capitalize(), get_python_type(v))}" for k, v in json_obj["args"].items())
    args_class = f"@dataclass\nclass {args_classname}:\n    {attributes}\n\n"
    command_class = f"@dataclass\nclass {classname}:\n    command: str\n    args: {args_classname}\n\n"
    return args_class + "\n" + command_class

def generate_python_function_from_class(classname: str, args_classname: str) -> str:
    return f"def {classname.lower()}(args: {args_classname}) -> {classname}:\n    return {classname}(command='{classname.lower()}', args=args)\n\n"

def main(filename: str) -> None:
    print("from dataclasses import dataclass")
    print("from typing import Any, List, Dict\n\n")
    json_obj = remove_comments_and_load_json(filename)
    nested_classes = {}
    classnames = []
    for command in json_obj:
        for k, v in command["args"].items():
            if isinstance(v, dict):
                nested_class, nested_classname = get_python_type(v, k.capitalize())
                print(nested_class)
                nested_classes[k.capitalize()] = nested_classname
    for command in json_obj:
        class_str = generate_dataclass_from_json(command, nested_classes)
        print(class_str)
        classname = command["command"].capitalize()
        args_classname = classname + "Args"
        classnames.append((classname, args_classname))
    for classname, args_classname in classnames:
        function_str = generate_python_function_from_class(classname, args_classname)
        print(function_str)

if __name__ == "__main__":
    main("commands.jsonc")  # JSONCファイルの名前をここに書く
