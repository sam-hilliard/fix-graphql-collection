#!/usr/bin/env python3

import pytest
import src.parse_collection as pc

# --- CORE LOGIC TESTS ---

def test_get_graphql_request_empty():
    """Should return None when the items list is empty."""
    assert pc.get_graphql_request([]) is None


def test_get_graphql_request_no_graphql():
    """Should return None if requests exist but none are in GraphQL mode."""
    items = [
        {"request": {"body": {"mode": "raw", "raw": "something else"}}}
    ]
    assert pc.get_graphql_request(items) is None


def test_get_graphql_request_flat_success():
    """Should successfully find and return a GraphQL payload in a flat list."""
    graphql_data = {"query": "query { getUser }", "variables": "{}"}
    items = [
        {"request": {"body": {"mode": "graphql", "graphql": graphql_data}}}
    ]
    assert pc.get_graphql_request(items) == graphql_data


def test_get_graphql_request_returns_first_match():
    """Should return the very first GraphQL payload found and stop traversing."""
    first_graphql = {"query": "query { first }"}
    second_graphql = {"query": "query { second }"}

    items = [
        {"request": {"body": {"mode": "graphql", "graphql": first_graphql}}},
        {"request": {"body": {"mode": "graphql", "graphql": second_graphql}}}
    ]
    assert pc.get_graphql_request(items) == first_graphql


# --- TRAVERSAL & EDGE CASE TESTS ---

def test_get_graphql_request_deeply_nested_success():
    """Should traverse deeply nested folders to locate a hidden GraphQL node."""
    graphql_data = {"query": "mutation { createUser }"}

    # Dynamically build a deep structure to thoroughly test recursion stability
    nested_items = [{"request": {"body": {"mode": "graphql", "graphql": graphql_data}}}]
    for i in range(10):
        nested_items = [{"name": f"Folder {i}", "item": nested_items}]

    assert pc.get_graphql_request(nested_items) == graphql_data


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
    assert pc.get_graphql_request([malformed_item]) is None
