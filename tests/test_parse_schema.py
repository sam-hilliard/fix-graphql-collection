import pytest
from unittest.mock import MagicMock
from graphql import GraphQLScalarType, GraphQLObjectType
import src.parse_schema as ps

# TESTS FOR get_custom_scalars()

def test_get_custom_scalars_filters_correctly(monkeypatch):
    # Create simple mock instances that pass isinstance(obj, GraphQLScalarType)
    custom_scalar_1 = MagicMock(spec=GraphQLScalarType)
    custom_scalar_1.name = "DateTime"

    custom_scalar_2 = MagicMock(spec=GraphQLScalarType)
    custom_scalar_2.name = "UUID"

    builtin_scalar = MagicMock(spec=GraphQLScalarType)
    builtin_scalar.name = "String"

    object_type = MagicMock(spec=GraphQLObjectType)
    object_type.name = "User"

    mock_schema = MagicMock()
    mock_schema.type_map = {
        "DateTime": custom_scalar_1,
        "UUID": custom_scalar_2,
        "String": builtin_scalar,
        "User": object_type
    }
    monkeypatch.setattr(ps, "build_client_schema", lambda data: mock_schema)

    def mock_is_specified(type_obj):
        return type_obj.name == "String"
    monkeypatch.setattr(ps, "is_specified_scalar_type", mock_is_specified)

    dummy_introspection = {"data": {"__schema": {}}}
    result = ps.get_custom_scalars(dummy_introspection)

    assert len(result) == 2
    assert "DateTime" in result
    assert "UUID" in result
    assert "String" not in result
    assert "User" not in result


# TESTS FOR main()

def test_main_execution_flow(monkeypatch, capsys):
    exported_file = None
    exported_data = None

    monkeypatch.setattr(ps, "load_json_file", lambda: {"dummy": "data"})

    def mock_export(filename, data):
        nonlocal exported_file, exported_data
        exported_file = filename
        exported_data = data
    monkeypatch.setattr(ps, "export_json_to_file", mock_export)

    monkeypatch.setattr(ps, "get_custom_scalars", lambda data: ["Email", "URL"])

    ps.main()

    assert exported_file == "custom_scalars.json"
    assert exported_data == {"Email": None, "URL": None}

    captured = capsys.readouterr()
    assert "Custom scalars saved to custom_scalars.json" in captured.out
    assert "Fill in the `null` values for the most accurate results" in captured.out
