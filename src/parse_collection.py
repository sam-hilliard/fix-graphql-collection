#!/usr/bin/env python3

import json

def get_graphql_request(items):

    if items is None:
        return None

    for item in items:
        if item is None or not isinstance(item, dict):
            continue

        if "item" in item:
            result = get_graphql_request(item["item"])
            if result:
                return result

        request = item.get("request", {})

        if not request:
            return None

        body = request.get("body", {})

        if body.get("mode") == "graphql" and "graphql" in body:
            return body["graphql"]

    return None
