#!/usr/bin/env python3

import sys
from pathlib import Path
from src.utils import load_introspective_json, export_json_to_file
from src.parse_schema import get_custom_scalars
from src.parse_collection import repair_collection

def output_custom_scalars(introspection_resp):
    custom_scalars = get_custom_scalars(introspection_resp)

    scalars_dict = {scalar: None for scalar in custom_scalars}
    output_filename = "custom_scalars.json"

    export_json_to_file(output_filename, scalars_dict)

    print(f"Custom scalars saved to {output_filename}")
    print("-> Action Required: Fill in the `null` values for the best results.")
    print("-> Then re-run this script to fully repair the collection.")

def main():
    introspection_resp = load_introspective_json()

    custom_scalars_path = Path("./custom_scalars.json")

    if not custom_scalars_path.is_file():
        output_custom_scalars(introspection_resp)
        sys.exit(0)

    collection_path = sys.argv[2]

    if not Path(collection_path).is_file():
        print(f"Error: Postman collection file '{collection_path}' not found.")
        print(f"Verify file placement or provide it explicitly: python {sys.argv[0]} introspection.json collection.json")
        sys.exit(1)

    print(f"Starting repair on '{collection_path}'...")
    repair_collection(collection_path, introspection_resp)
    print("Process complete! Check the output directory for your repaired file.")

if __name__ == '__main__':
   main()
