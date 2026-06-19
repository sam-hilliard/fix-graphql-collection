#!/usr/bin/env python3

import json
import os
from src.utils import import_json_from_file
import src.parse_schema as pc
from src.constants import GRAPHQL_SCALARS

from graphql import (
    build_client_schema,
    GraphQLScalarType,
    GraphQLInputObjectType,
    GraphQLInputField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLInt,
    GraphQLList,
    GraphQLEnumType
)

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

def generate_sample_value(gql_type, scalar_mappings, seen=None):
    seen = seen or set()

    # unwrap !
    if isinstance(gql_type, GraphQLNonNull):
        return generate_sample_value(
            gql_type.of_type,
            scalar_mappings,
            seen,
        )

    # handle lists
    if isinstance(gql_type, GraphQLList):
        return [
            generate_sample_value(
                gql_type.of_type,
                scalar_mappings,
                seen,
            )
        ]

    # custom enum
    if isinstance(gql_type, GraphQLEnumType):
        return next(iter(gql_type.values))

    # scalar / custom scalar
    if isinstance(gql_type, GraphQLScalarType):
        return scalar_mappings.get(gql_type.name)

    # input object
    if isinstance(gql_type, GraphQLInputObjectType):
        if gql_type.name in seen:
            return {}

        seen.add(gql_type.name)

        result = {}

        for field_name, field in gql_type.fields.items():
            # only populate required fields
            if isinstance(field.type, GraphQLNonNull):
                result[field_name] = generate_sample_value(
                    field.type,
                    scalar_mappings,
                    seen.copy(),
                )

        return result

    return None

def repair_vars(introspection_resp, item):
    graphql_request = get_graphql_request(item)
    if not graphql_request:
        return item

    graphql_query = graphql_request.get("query", "")
    custom_scalars = import_json_from_file("./custom_scalars.json") or {}
    required_vars = pc.get_required_vars(introspection_resp, graphql_query)


    filled_vars = {}
    scalar_mappings = {**GRAPHQL_SCALARS, **custom_scalars}

    schema = build_client_schema(introspection_resp["data"])

    for var_name, var_type in required_vars.items():
        clean_type = (
            var_type
            .replace("!", "")
            .replace("[", "")
            .replace("]", "")
        )

        gql_type = schema.get_type(clean_type)

        if gql_type:
            filled_vars[var_name] = generate_sample_value(
                gql_type,
                scalar_mappings,
            )
        else:
            filled_vars[var_name] = scalar_mappings.get(clean_type)

    graphql_request["variables"] = json.dumps(filled_vars, indent=2)

    if hasattr(item, 'request') and hasattr(item.request, 'body'):
        item.request.body.graphql = graphql_request
    else:
        item.setdefault("request", {}).setdefault("body", {})["graphql"] = graphql_request

    return item

def process_items(items, introspection_resp):
    """Recursively walks through Postman folders and requests."""
    if not isinstance(items, list):
        return

    for item in items:
        if "item" in item:
            process_items(item["item"], introspection_resp)
        elif "request" in item:
            repair_vars(introspection_resp, item)

def repair_collection(collection_path, introspection_resp):
    """
    Loads collection, repairs its GraphQL variables based on introspection,
    and saves to a new path to avoid overwriting.
    """
    with open(collection_path, "r", encoding="utf-8") as f:
        collection = json.load(f)

    if "item" in collection:
        process_items(collection["item"], introspection_resp)

    base, ext = os.path.splitext(collection_path)
    output_path = f"{base}_repaired{ext}"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2)

    print(f"Repaired collection saved to: {output_path}")
