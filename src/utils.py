#!/usr/bin/env python3

import sys
import json

def import_json_from_file(path):
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{path}' was not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: '{path}' is not a valid JSON file.")
        sys.exit(1)

def load_introspective_json():
    if len(sys.argv) < 2:
        print("Error: Missing introspection file argument.")
        print(f"Usage: python {sys.argv[0]} <path_to_introspection.json> [path_to_collection.json]")
        sys.exit(1)

    file_path = sys.argv[1]
    return import_json_from_file(file_path)

def export_json_to_file(output_filename, json_data):
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4)
