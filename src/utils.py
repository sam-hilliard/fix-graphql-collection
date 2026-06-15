#!/usr/bin/env python3

import sys
import json

def load_introspective_json():

    if len(sys.argv) < 2:
        print("Error: Please provide the path to the introspective JSON file.")
        print(f"Usage: python {sys.argv[0]} <path_to_file.json>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            introspection_data = json.load(file)

        return introspection_data

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        sys.exit(1)


def export_json_to_file(output_filename, json_data):
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4)

def import_json_from_file(path):

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(path)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{file_path}' is not a valid JSON file.")
        sys.exit(1)
