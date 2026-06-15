#!/usr/bin/env python3

#!/usr/bin/env python3

import pytest
import src.parse_collection as pc

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
