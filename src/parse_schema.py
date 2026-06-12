#!/usr/bin/env python3

from graphql import build_client_schema, GraphQLScalarType, is_specified_scalar_type
import json
from .utils import load_json_file, export_json_to_file

def get_custom_scalars(introspection_resp):

    schema = build_client_schema(introspection_resp["data"])

    custom_scalars = [
        type_name for type_name, type_obj in schema.type_map.items()
        if isinstance(type_obj, GraphQLScalarType) and not is_specified_scalar_type(type_obj)
    ]

    return custom_scalars


def main():
    introspection_data = load_json_file()
    custom_scalars = get_custom_scalars(introspection_data)

    scalars_dict = {scalar: None for scalar in custom_scalars}
    output_filename = "custom_scalars.json"

    export_json_to_file(output_filename, scalars_dict)

    print(f"Custom scalars saved to {output_filename}")
    print(f"Fill in the `null` values for the most accurate results")

if __name__ == '__main__':
    main()
