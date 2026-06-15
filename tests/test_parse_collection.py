#!/usr/bin/env python3

import json
import pytest
from unittest.mock import patch, mock_open  # Added mock_open import
import src.parse_collection as pc

# --- GET GRAPHQL TESTS ---

def test_get_graphql_request_empty():
    """Should return None when an empty dictionary is provided."""
    assert pc.get_graphql_request({}) is None


def test_get_graphql_request_no_graphql():
    """Should return None if the request exists but is not in GraphQL mode."""
    item = {"request": {"body": {"mode": "raw", "raw": "something else"}}}
    assert pc.get_graphql_request(item) is None


def test_get_graphql_request_flat_success():
    """Should successfully find and return a GraphQL payload from a single item."""
    graphql_data = {"query": "query { getUser }", "variables": "{}"}
    item = {"request": {"body": {"mode": "graphql", "graphql": graphql_data}}}

    assert pc.get_graphql_request(item) == graphql_data


def test_get_graphql_request_returns_first_match():
    """Should return the GraphQL payload of the parent/first matching node when traversing."""
    first_graphql = {"query": "query { first }"}
    second_graphql = {"query": "query { second }"}

    # Nesting the second item inside the first item's sub-folder structure
    item = {
        "request": {"body": {"mode": "graphql", "graphql": first_graphql}},
        "item": {
            "request": {"body": {"mode": "graphql", "graphql": second_graphql}}
        }
    }
    assert pc.get_graphql_request(item) == first_graphql


def test_get_graphql_request_deeply_nested_success():
    """Should traverse deeply nested item object folders to locate a hidden GraphQL node."""
    graphql_data = {"query": "mutation { createUser }"}

    # Dynamically build a deep structure of nested dictionaries to test recursion stability
    nested_item = {"request": {"body": {"mode": "graphql", "graphql": graphql_data}}}
    for i in range(10):
        nested_item = {"name": f"Folder {i}", "item": nested_item}

    assert pc.get_graphql_request(nested_item) == graphql_data


@pytest.mark.parametrize(
    "malformed_item",
    [
        {"name": "Empty Item, no request or sub-items"},
        {"request": {}},
        {"request": {"body": {"mode": "graphql"}}},
        {"request": None},
        {"item": None},
    ],
    ids=["no_keys", "missing_body", "missing_graphql", "null_request", "null_item"]
)
def test_get_graphql_request_malformed_structures(malformed_item):
    """Should gracefully return None for malformed structures without crashing."""
    assert pc.get_graphql_request(malformed_item) is None


def test_get_graphql_request_invalid_type_input():
    """Should return None immediately if input is a list, string, or non-dict."""
    assert pc.get_graphql_request([]) is None
    assert pc.get_graphql_request("invalid_string_input") is None


# --- REPAIR VARIABLES TESTS ---

def test_repair_vars_dict_item_success():
    """Should successfully map scalars to variables on a dict-based item."""
    mock_req = {"query": "query { getUser }", "variables": "{}"}

    with patch(f"{pc.__name__}.get_graphql_request", return_value=mock_req), \
         patch(f"{pc.__name__}.import_json_from_file", return_value={}), \
         patch(f"{pc.__name__}.pc.get_required_vars", return_value={"username": "String", "age": "Int"}), \
         patch(f"{pc.__name__}.GRAPHQL_SCALARS", {"String": "default_text", "Int": 0}):

        test_item = {"request": {"body": {"graphql": {}}}}
        result = pc.repair_vars("mock_introspection", test_item)

        # Fix: Parse the stringified JSON output back to dictionary to evaluate
        variables_str = result["request"]["body"]["graphql"]["variables"]
        assert isinstance(variables_str, str)

        parsed_vars = json.loads(variables_str)
        expected_vars = {"username": "default_text", "age": 0}
        assert parsed_vars == expected_vars


def test_repair_vars_strips_graphql_modifiers():
    """Should strip non-null (!) and list ([]) modifiers from types before mapping."""
    mock_req = {"query": "query { getTags }", "variables": "{}"}

    with patch(f"{pc.__name__}.get_graphql_request", return_value=mock_req), \
         patch(f"{pc.__name__}.import_json_from_file", return_value={}), \
         patch(f"{pc.__name__}.pc.get_required_vars", return_value={"tags": "[String!]", "primaryId": "ID!"}), \
         patch(f"{pc.__name__}.GRAPHQL_SCALARS", {"String": "placeholder", "ID": "000"}):

        test_item = {"request": {"body": {"graphql": {}}}}
        result = pc.repair_vars("mock_introspection", test_item)

        # Fix: Parse the stringified JSON output back to dictionary to evaluate
        variables_str = result["request"]["body"]["graphql"]["variables"]
        assert isinstance(variables_str, str)

        parsed_vars = json.loads(variables_str)
        assert parsed_vars["tags"] == "placeholder"
        assert parsed_vars["primaryId"] == "000"


def test_repair_vars_custom_scalars_override():
    """Should prioritize values from custom_scalars.json over base definitions."""
    mock_req = {"query": "query { custom }", "variables": "{}"}

    with patch(f"{pc.__name__}.get_graphql_request", return_value=mock_req), \
         patch(f"{pc.__name__}.pc.get_required_vars", return_value={"email": "Email", "name": "String"}), \
         patch(f"{pc.__name__}.GRAPHQL_SCALARS", {"String": "base_text"}), \
         patch(f"{pc.__name__}.import_json_from_file", return_value={"String": "custom_text", "Email": "user@domain.com"}):

        test_item = {"request": {"body": {"graphql": {}}}}
        result = pc.repair_vars("mock_introspection", test_item)

        # Fix: Parse the stringified JSON output back to dictionary to evaluate
        variables_str = result["request"]["body"]["graphql"]["variables"]
        assert isinstance(variables_str, str)

        parsed_vars = json.loads(variables_str)
        assert parsed_vars["name"] == "custom_text"
        assert parsed_vars["email"] == "user@domain.com"


def test_repair_vars_unknown_scalar_defaults_none():
    """Should assign None to variables when the GraphQL scalar is unmapped."""
    mock_req = {"query": "query { unknown }", "variables": "{}"}

    with patch(f"{pc.__name__}.get_graphql_request", return_value=mock_req), \
         patch(f"{pc.__name__}.import_json_from_file", return_value={}), \
         patch(f"{pc.__name__}.pc.get_required_vars", return_value={"secretKey": "UnknownType"}), \
         patch(f"{pc.__name__}.GRAPHQL_SCALARS", {"String": "text"}):

        test_item = {"request": {"body": {"graphql": {}}}}
        result = pc.repair_vars("mock_introspection", test_item)

        # Fix: Parse the stringified JSON output back to dictionary to evaluate
        variables_str = result["request"]["body"]["graphql"]["variables"]
        assert isinstance(variables_str, str)

        parsed_vars = json.loads(variables_str)
        assert parsed_vars["secretKey"] is None


# --- PROCESS ITEMS TESTS ---

def test_process_items_recursively_calls_repair_vars():
    """Should traverse nested arrays and call repair_vars on items with requests."""
    collection_items = [
        {
            "name": "Folder",
            "item": [
                {
                    "name": "Nested Request",
                    "request": {"body": {"mode": "graphql", "graphql": {"query": "{ hello }"}}}
                }
            ]
        },
        {
            "name": "Root Request",
            "request": {"body": {"mode": "graphql", "graphql": {"query": "{ world }"}}}
        }
    ]

    with patch(f"{pc.__name__}.repair_vars") as mock_repair:
        pc.process_items(collection_items, "mock_introspection")
        assert mock_repair.call_count == 2


def test_process_items_safely_skips_invalid_types():
    """Should return early and not raise errors if provided non-list items."""
    with patch(f"{pc.__name__}.repair_vars") as mock_repair:
        pc.process_items("not_a_list", "mock_introspection")
        mock_repair.assert_not_called()


# --- REPAIR COLLECTION TESTS ---

def test_repair_collection_e2e_flow():
    """Should open file, execute recursive updates, serialize variables to JSON string, and save."""
    mock_collection = {
        "info": {"name": "Test Collection"},
        "item": [
            {
                "name": "getUser",
                "request": {
                    "body": {
                        "mode": "graphql",
                        "graphql": {
                            "query": "query { getUser }"
                        }
                    }
                }
            }
        ]
    }

    mock_introspection = {"types": []}

    with patch("builtins.open", mock_open(read_data=json.dumps(mock_collection))) as mock_file, \
         patch(f"{pc.__name__}.import_json_from_file", return_value={}), \
         patch(f"{pc.__name__}.pc.get_required_vars", return_value={"id": "ID!"}), \
         patch(f"{pc.__name__}.GRAPHQL_SCALARS", {"ID": "000"}):

        pc.repair_collection("collection.json", mock_introspection)

        mock_file.assert_any_call("collection.json", "r", encoding="utf-8")
        mock_file.assert_any_call("collection_repaired.json", "w", encoding="utf-8")

        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        saved_json = json.loads(written_data)

        graphql_block = saved_json["item"][0]["request"]["body"]["graphql"]
        assert isinstance(graphql_block["variables"], str)

        parsed_variables = json.loads(graphql_block["variables"])
        assert parsed_variables["id"] == "000"


def test_repair_collection_missing_item_key():
    """Should gracefully write copy out even if the collection root has no item list."""
    mock_collection = {"info": {"name": "Empty collection block"}}
