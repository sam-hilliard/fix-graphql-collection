#!/usr/bin/env python3

import json
from unittest.mock import patch, mock_open, MagicMock

import pytest

from graphql import (
    GraphQLScalarType,
    GraphQLInputObjectType,
    GraphQLInputField,
    GraphQLNonNull,
    GraphQLString,
    GraphQLInt,
    GraphQLList,
)

import src.parse_collection as pc



# --- GET GRAPHQL TESTS ---

def test_get_graphql_request_empty():
    assert pc.get_graphql_request({}) is None


def test_get_graphql_request_no_graphql():
    item = {
        "request": {
            "body": {
                "mode": "raw",
                "raw": "something else",
            }
        }
    }

    assert pc.get_graphql_request(item) is None


def test_get_graphql_request_flat_success():
    graphql_data = {
        "query": "query { getUser }",
        "variables": "{}",
    }

    item = {
        "request": {
            "body": {
                "mode": "graphql",
                "graphql": graphql_data,
            }
        }
    }

    assert pc.get_graphql_request(item) == graphql_data


def test_get_graphql_request_returns_first_match():
    first = {"query": "query { first }"}
    second = {"query": "query { second }"}

    item = {
        "request": {
            "body": {
                "mode": "graphql",
                "graphql": first,
            }
        },
        "item": {
            "request": {
                "body": {
                    "mode": "graphql",
                    "graphql": second,
                }
            }
        },
    }

    assert pc.get_graphql_request(item) == first


def test_get_graphql_request_invalid_type_input():
    assert pc.get_graphql_request([]) is None
    assert pc.get_graphql_request("invalid") is None


# --- SAMPLE GENERATION TESTS ---

def test_generate_sample_value_scalar():
    result = pc.generate_sample_value(
        GraphQLNonNull(GraphQLString),
        {"String": "hello"},
    )

    assert result == "hello"


def test_generate_sample_value_required_nested_input():
    address = GraphQLInputObjectType(
        "AddressInput",
        {
            "city": GraphQLInputField(
                GraphQLNonNull(GraphQLString)
            ),
            "zip": GraphQLInputField(GraphQLString),
        },
    )

    user = GraphQLInputObjectType(
        "UserInput",
        {
            "name": GraphQLInputField(
                GraphQLNonNull(GraphQLString)
            ),
            "age": GraphQLInputField(
                GraphQLNonNull(GraphQLInt)
            ),
            "address": GraphQLInputField(
                GraphQLNonNull(address)
            ),
        },
    )

    result = pc.generate_sample_value(
        user,
        {
            "String": "text",
            "Int": 1,
        },
    )

    assert result == {
        "name": "text",
        "age": 1,
        "address": {
            "city": "text",
        },
    }


def test_generate_sample_value_list():
    result = pc.generate_sample_value(
        GraphQLList(GraphQLString),
        {"String": "value"},
    )

    assert result == ["value"]


# --- REPAIR VARIABLES TESTS ---

def test_repair_vars_dict_item_success():

    mock_req = {
        "query": "query { getUser }",
        "variables": "{}",
    }

    schema = MagicMock()

    schema.get_type.side_effect = {
        "String": GraphQLString,
        "Int": GraphQLInt,
    }.get


    with patch(
        "src.parse_collection.get_graphql_request",
        return_value=mock_req,
    ), \
    patch(
        "src.parse_collection.import_json_from_file",
        return_value={},
    ), \
    patch(
        "src.parse_collection.pc.get_required_vars",
        return_value={
            "username": "String",
            "age": "Int",
        },
    ), \
    patch(
        "src.parse_collection.build_client_schema",
        return_value=schema,
    ), \
    patch(
        "src.parse_collection.GRAPHQL_SCALARS",
        {
            "String": "default_text",
            "Int": 0,
        },
    ):

        result = pc.repair_vars(
            {"data": {}},
            {
                "request": {
                    "body": {
                        "graphql": {}
                    }
                }
            },
        )

        variables = json.loads(
            result["request"]["body"]["graphql"]["variables"]
        )

        assert variables == {
            "username": "default_text",
            "age": 0,
        }


def test_repair_vars_unknown_scalar():

    mock_req = {
        "query": "query { unknown }",
        "variables": "{}",
    }

    schema = MagicMock()
    schema.get_type.return_value = None

    with patch(
        "src.parse_collection.get_graphql_request",
        return_value=mock_req,
    ), \
    patch(
        "src.parse_collection.pc.get_required_vars",
        return_value={
            "secret": "Unknown",
        },
    ), \
    patch(
        "src.parse_collection.build_client_schema",
        return_value=schema,
    ), \
    patch(
        "src.parse_collection.GRAPHQL_SCALARS",
        {},
    ), \
    patch(
        "src.parse_collection.import_json_from_file",
        return_value={},
    ):

        result = pc.repair_vars(
            {"data": {}},
            {
                "request": {
                    "body": {
                        "graphql": {}
                    }
                }
            },
        )

        variables = json.loads(
            result["request"]["body"]["graphql"]["variables"]
        )

        assert variables["secret"] is None


# --- PROCESS ITEMS ---

def test_process_items_recursively_calls_repair_vars():

    items = [
        {
            "item": [
                {
                    "request": {}
                }
            ]
        }
    ]

    with patch(
        "src.parse_collection.repair_vars"
    ) as mock_repair:

        pc.process_items(
            items,
            {"data": {}},
        )

        mock_repair.assert_called_once()


# --- REPAIR COLLECTION ---

def test_repair_collection_e2e_flow():

    collection = {
        "item": [
            {
                "request": {
                    "body": {
                        "mode": "graphql",
                        "graphql": {
                            "query": "query { user }"
                        }
                    }
                }
            }
        ]
    }

    with patch(
        "builtins.open",
        mock_open(
            read_data=json.dumps(collection)
        ),
    ) as file, \
    patch(
        "src.parse_collection.process_items"
    ) as process:

        pc.repair_collection(
            "collection.json",
            {"data": {}},
        )

        process.assert_called_once()

        file.assert_any_call(
            "collection.json",
            "r",
            encoding="utf-8",
        )
