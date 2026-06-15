#!/usr/bin/env python3

import json
from src.utils import import_json_from_file
import src.parse_schema as pc
from src.constants import GRAPHQL_SCALARS

def get_graphql_request(item):

    if item is None or not isinstance(item, dict):
        return None

    request = item.get("request", {})
    if request:
        body = request.get("body", {})
        if body.get("mode") == "graphql" and "graphql" in body:
            return body["graphql"]

    if "item" in item:
        result = get_graphql_request(item["item"])
        if result:
            return result

    return None



def repair_vars(introspection_resp, item):

    graphql_request = get_graphql_request(item)
    graphql_query = graphql_request["query"]
    custom_scalars = import_json_from_file("./custom_scalars.json")
    required_vars = pc.get_required_vars(introspection_resp, graphql_query)

    filled_vars = {}

    scalar_mappings = {**GRAPHQL_SCALARS, **custom_scalars}

    for var_name, var_type in required_vars.items():
        clean_type = var_type.replace("!", "").replace("[", "").replace("]", "")

        filled_vars[var_name] = scalar_mappings.get(clean_type, None)

    graphql_request["variables"] = filled_vars

    if hasattr(item, 'request') and hasattr(item.request, 'body'):
        item.request.body.graphql = graphql_request
    else:
        item["request"]["body"]["graphql"] = graphql_request

    return item
