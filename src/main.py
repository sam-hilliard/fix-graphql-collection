#!/usr/bin/env python3

from utils import load_introspective_json, export_json_to_file
from parse_schema import get_custom_scalars
from pathlib import Path

def output_custom_scalars(introspection_resp):
    custom_scalars = get_custom_scalars(introspection_resp)

    scalars_dict = {scalar: None for scalar in custom_scalars}
    output_filename = "custom_scalars.json"

    export_json_to_file(output_filename, scalars_dict)

    print(f"Custom scalars saved to {output_filename}")
    print(f"Fill in the `null` values for the most accurate results")
    print("Re-run to repair collection")


def main():
    introspection_resp = load_introspective_json()

    custom_scalars_path = Path("./custom_scalars.json")
    if custom_scalars_path.is_file():
        output_custom_scalars(introspection_resp)
        sys.exit(0)




if __name__ == '__main__':
   main()
