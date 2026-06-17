#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from src.utils import import_json_from_file, export_json_to_file
from src.parse_schema import get_custom_scalars
from src.parse_collection import repair_collection

def output_custom_scalars(introspection_resp):

    scalars_dict = {scalar: None for scalar in custom_scalars}
    output_filename = "custom_scalars.json"

    export_json_to_file(output_filename, scalars_dict)

    print(f"Custom scalars saved to {output_filename}")
    print("-> Action Required: Fill in the `null` values for the best results.")
    print("-> Then re-run this script to fully repair the collection.")

def main():
    parser = argparse.ArgumentParser(
        description="Repair a Postman GraphQL collection using schema introspection data."
    )

    parser.add_argument(
        "-i", "--introspection",
        help="Path to the introspection JSON response file."
    )

    parser.add_argument(
        "-c", "--collection",
        help="Path to the Postman collection JSON file."
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if not args.introspection:
        print("Error: Missing required introspection.json file via '-i' or '--introspection' flag.")
        sys.exit(1)

    introspection_resp = import_json_from_file(args.introspection)

    custom_scalars_path = Path("./custom_scalars.json")

    if not custom_scalars_path.is_file():
        output_custom_scalars(introspection_resp)
        sys.exit(0)

    if not args.collection:
        print("Error: Missing required collection file via '-c' or '--collection' flag.")
        sys.exit(1)

    collection_path = Path(args.collection_path if hasattr(args, 'collection_path') else args.collection)

    if not collection_path.is_file():
        print(f"Error: Postman collection file '{collection_path}' not found.")
        sys.exit(1)

    print(f"Starting repair on '{collection_path}'...")
    repair_collection(str(collection_path), introspection_resp)
    print("Process complete! Check the output directory for your repaired file.")

if __name__ == '__main__':
   main()
