#!/usr/bin/env python3

from graphql import build_client_schema, GraphQLScalarType, is_specified_scalar_type
import json
import sys

def get_custom_scalars(introspection_resp):

    schema = build_client_schema(introspection_resp["data"])

    custom_scalars = [
        type_name for type_name, type_obj in schema.type_map.items()
        if isinstance(type_obj, GraphQLScalarType) and not is_specified_scalar_type(type_obj)
    ]

    print(custom_scalars)

def load_file():

    if len(sys.argv) < 2:
        print("Error: Please provide the path to the JSON file.")
        print("Usage: python script.py <path_to_file.json>")
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


def main():
    introspection_data = load_file()
    get_custom_scalars(introspection_data)

if __name__ == '__main__':
    main()
