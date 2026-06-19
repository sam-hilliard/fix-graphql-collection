#!/usr/bin/env python3

import json
import pytest
import sys
from src.utils import import_json_from_file, export_json_to_file

# Import JSON tests

def test_import_json_from_file_success(tmp_path):
    """Test that valid JSON is loaded and returned as Python data."""

    input_file = tmp_path / "input.json"

    data = {
        "user": "alice",
        "active": True,
        "roles": ["admin"],
    }

    with open(input_file, "w", encoding="utf-8") as f:
        json.dump(data, f)

    result = import_json_from_file(str(input_file))

    assert result == data


def test_import_json_from_file_missing_file(tmp_path, capsys):
    """Test that missing files print an error and exit."""

    missing_file = tmp_path / "does_not_exist.json"

    with pytest.raises(SystemExit) as exc:
        import_json_from_file(str(missing_file))

    assert exc.value.code == 1

    captured = capsys.readouterr()
    assert "was not found" in captured.out


def test_import_json_from_file_invalid_json(tmp_path, capsys):
    """Test that malformed JSON prints an error and exits."""

    bad_file = tmp_path / "invalid.json"

    bad_file.write_text(
        "{ invalid json }",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as exc:
        import_json_from_file(str(bad_file))

    assert exc.value.code == 1

    captured = capsys.readouterr()
    assert "is not a valid JSON file" in captured.out


# Export JSON tests

def test_export_json_to_file(tmp_path):
    """Test that dictionary data is successfully written to a JSON file."""

    output_file = tmp_path / "output.json"
    data_to_export = {
        "user": "alice",
        "active": True,
    }

    export_json_to_file(
        str(output_file),
        data_to_export,
    )

    assert output_file.exists()

    with open(
        output_file,
        "r",
        encoding="utf-8",
    ) as f:
        saved_data = json.load(f)

    assert saved_data == data_to_export

def test_export_json_to_file(tmp_path):
    """Test that dictionary data is successfully written to a JSON file."""
    # Define target path in temp folder and dummy data
    output_file = tmp_path / "output.json"
    data_to_export = {"user": "alice", "active": True}

    # Run the exporter
    export_json_to_file(str(output_file), data_to_export)

    # Read it back manually to verify the contents and structure
    assert output_file.exists()

    with open(output_file, "r", encoding="utf-8") as f:
        saved_data = json.load(f)

    assert saved_data == data_to_export
