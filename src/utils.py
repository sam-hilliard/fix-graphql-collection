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

def export_json_to_file(output_filename, json_data):
    with open(output_filename, "w", encoding="utf-8") as file:
        json.dump(json_data, file, indent=4)
