#!/usr/bin/env python3

import json

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
