#!/usr/bin/env python3

from utils import load_introspective_json, export_json_to_file
from parse_schema import get_custom_scalars

def output_custom_scalars(introspection_resp):
    custom_scalars = get_custom_scalars(introspection_resp)

    scalars_dict = {scalar: None for scalar in custom_scalars}
    output_filename = "custom_scalars.json"

    export_json_to_file(output_filename, scalars_dict)

    print(f"Custom scalars saved to {output_filename}")
    print(f"Fill in the `null` values for the most accurate results")


def main():
    introspection_resp = load_introspective_json()
    output_custom_scalars(introspection_resp)


if __name__ == '__main__':
   main()
