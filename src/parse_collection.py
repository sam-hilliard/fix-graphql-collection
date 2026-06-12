#!/usr/bin/env python3

import json
from utils import load_json_file


def get_graphql_request(items):
    for item in items:
        if "item" in item:
            result = get_graphql_request(item["item"])
            if result:
                return result

        request = item.get("request", {})
        body = request.get("body", {})

        if body.get("mode") == "graphql" and "graphql" in body:
            return body["graphql"]

    return None


def main():
    collection_data = load_json_file()

    collection_items = collection_data.get("item", [])

    graphql_payload = get_graphql_request(collection_items)

    if graphql_payload:
        query = graphql_payload.get("query", "No query found")
        variables = graphql_payload.get("variables", "No variables found")

        print("=== FIRST GRAPHQL QUERY ===")
        print(query)

        print("\n=== VARIABLES ===")
        print(variables)
    else:
        print("No GraphQL requests found in the collection.")

if __name__ == '__main__':
    main()
