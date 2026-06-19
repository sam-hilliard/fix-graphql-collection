#!/usr/bin/env python3

import pytest
from unittest.mock import MagicMock, patch

from graphql import GraphQLScalarType, GraphQLObjectType

import src.parse_schema as ps


@patch("src.parse_schema.is_specified_scalar_type")
@patch("src.parse_schema.build_client_schema")
def test_get_custom_scalars_filters_correctly(
    mock_build_schema,
    mock_is_specified,
):
    """
    Test that built-in scalars and object types are filtered out,
    leaving only custom scalars.
    """

    custom_scalar_1 = MagicMock(spec=GraphQLScalarType)
    custom_scalar_1.__class__ = GraphQLScalarType
    custom_scalar_1.name = "DateTime"

    custom_scalar_2 = MagicMock(spec=GraphQLScalarType)
    custom_scalar_2.__class__ = GraphQLScalarType
    custom_scalar_2.name = "UUID"

    builtin_scalar = MagicMock(spec=GraphQLScalarType)
    builtin_scalar.__class__ = GraphQLScalarType
    builtin_scalar.name = "String"

    object_type = MagicMock(spec=GraphQLObjectType)
    object_type.__class__ = GraphQLObjectType
    object_type.name = "User"

    mock_schema = MagicMock()
    mock_schema.type_map = {
        "DateTime": custom_scalar_1,
        "UUID": custom_scalar_2,
        "String": builtin_scalar,
        "User": object_type,
    }

    mock_build_schema.return_value = mock_schema

    mock_is_specified.side_effect = (
        lambda type_obj: type_obj.name == "String"
    )

    dummy_introspection = {
        "data": {
            "__schema": {}
        }
    }

    result = ps.get_custom_scalars(dummy_introspection)

    assert result == [
        "DateTime",
        "UUID",
    ]

    mock_build_schema.assert_called_once_with(
        dummy_introspection["data"]
    )


@patch("src.parse_schema.build_client_schema")
def test_get_required_vars_extracts_non_null_variables(
    mock_build_schema,
):
    """
    Test that variables with ! and no defaults are captured.
    """

    mock_build_schema.return_value = MagicMock()

    introspection_data = {
        "data": {
            "__schema": {}
        }
    }

    payload = """
        query GetUser($id: ID!, $limit: Int = 10) {
            user(id: $id) {
                name
            }
        }
    """

    result = ps.get_required_vars(
        introspection_data,
        payload,
    )

    assert result == {
        "id": "ID!"
    }

    mock_build_schema.assert_called_once_with(
        introspection_data["data"]
    )
