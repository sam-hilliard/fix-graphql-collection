#!/usr/bin/env python3

import pytest
import src.parse_collection as pc
from src.utils import load_json_file

# Tests for get_graphql_request() (Core Logic & Edge Cases)

def test_get_graphql_request_empty():
    """Should return None when the items list is empty."""
    assert pc.get_graphql_request([]) is None


def test_get_graphql_request_no_graphql():
    """Should return None if requests exist but none are in GraphQL mode."""
    items = [
        {
            "request": {
                "body": {
                    "mode": "raw",
                    "raw": "something else"
                }
            }
        }
    ]
    assert pc.get_graphql_request(items) is None


def test_get_graphql_request_flat_success():
    """Should successfully find and return a GraphQL payload in a flat list."""
    graphql_data = {"query": "query { getUser }", "variables": "{}"}
    items = [
        {
            "request": {
                "body": {
                    "mode": "graphql",
                    "graphql": graphql_data
                }
            }
        }
    ]
    assert pc.get_graphql_request(items) == graphql_data


def test_get_graphql_request_recursive_nested_success():
    """Should traverse multiple layers of nested folders ('item' keys) to find GraphQL."""
    graphql_data = {"query": "mutation { createUser }", "variables": "{}"}

    nested_items = [
        {
            "name": "Root Folder",
            "item": [
                {
                    "name": "Sub Folder",
                    "item": [
                        {
                            "name": "GraphQL Request",
                            "request": {
                                "body": {
                                    "mode": "graphql",
                                    "graphql": graphql_data
                                }
                            }
                        }
                    ]
                }
            ]
        }
    ]
    assert pc.get_graphql_request(nested_items) == graphql_data


def test_get_graphql_request_malformed_structures():
    """Should gracefully handle dictionary schemas missing standard keys without crashing."""
    broken_items = [
        {"name": "Empty Item, no request or sub-items"},
        {"request": {}},  # Missing 'body'
        {"request": {"body": {"mode": "graphql"}}}  # Missing 'graphql' payload key
    ]
    assert pc.get_graphql_request(broken_items) is None


# Tests for main() (Execution Flow, Defaults, & Console Output)

def test_main_with_perfect_graphql_payload(monkeypatch, capsys):
    """Should print the explicit query and variables when complete data is loaded."""
    mock_data = {
        "item": [
            {
                "request": {
                    "body": {
                        "mode": "graphql",
                        "graphql": {
                            "query": "query MyQuery { id }",
                            "variables": '{"id": 1}'
                        }
                    }
                }
            }
        ]
    }
    # Mock load_json_file to return our mock dictionary
    monkeypatch.setattr(pc, "load_json_file", lambda: mock_data)

    pc.main()
    captured = capsys.readouterr()

    assert "=== FIRST GRAPHQL QUERY ===" in captured.out
    assert "query MyQuery { id }" in captured.out
    assert "=== VARIABLES ===" in captured.out
    assert '{"id": 1}' in captured.out


def test_main_with_missing_keys_fallback_defaults(monkeypatch, capsys):
    """Should use safety string defaults if the graphql block exists but lacks keys."""
    # The graphql dictionary exists, but contains no 'query' or 'variables' keys
    mock_data = {
        "item": [
            {
                "request": {
                    "body": {
                        "mode": "graphql",
                        "graphql": {}
                    }
                }
            }
        ]
    }
    monkeypatch.setattr(pc, "load_json_file", lambda: mock_data)

    pc.main()
    captured = capsys.readouterr()

    # Assert that fallback string defaults from your main() logic are displayed safely
    assert "No GraphQL requests found in the collection." in captured.out


def test_main_no_graphql_found(monkeypatch, capsys):
    """Should print a friendly message if the collection has absolutely no GraphQL requests."""
    mock_data = {"item": []}
    monkeypatch.setattr(pc, "load_json_file", lambda: mock_data)

    pc.main()
    captured = capsys.readouterr()

    assert "No GraphQL requests found in the collection." in captured.out
