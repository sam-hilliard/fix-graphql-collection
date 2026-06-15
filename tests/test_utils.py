#!/usr/bin/env python3

import json
import pytest
import sys
from src.utils import load_introspective_json, export_json_to_file

# Load JSON Tests

def test_load_introspective_json_missing_argument(monkeypatch):
    """Test that the script exits if no file argument is passed."""
    # Simulate running the script with NO arguments: ['json_utils.py']
    monkeypatch.setattr(sys, "argv", ["json_utils.py"])

    # Assert that sys.exit(1) is raised
    with pytest.raises(SystemExit) as exc_info:
        load_introspective_json()
    assert exc_info.value.code == 1


def test_load_introspective_json_success(monkeypatch, tmp_path):
    """Test successful JSON loading using a temporary file."""
    dummy_data = {"status": "success", "items":[]}
    test_file = tmp_path / "valid.json"
    test_file.write_text(json.dumps(dummy_data))

    monkeypatch.setattr(sys, "argv", ["json_utils.py", str(test_file)])

    result = load_introspective_json()
    assert result == dummy_data


def test_load_introspective_json_not_found(monkeypatch):
    """Test that the script exits safely if the file does not exist."""
    # Simulate targeting a nonexistent file
    monkeypatch.setattr(sys, "argv", ["json_utils.py", "fake_file.json"])

    with pytest.raises(SystemExit) as exc_info:
        load_introspective_json()
    assert exc_info.value.code == 1


def test_load_introspective_json_invalid_json(monkeypatch, tmp_path):
    """Test that the script catches malformed/broken JSON syntax."""
    # Create a file with broken JSON syntax
    test_file = tmp_path / "broken.json"
    test_file.write_text("{ broken javascript object literal }")

    monkeypatch.setattr(sys, "argv", ["json_utils.py", str(test_file)])

    with pytest.raises(SystemExit) as exc_info:
        load_introspective_json()
    assert exc_info.value.code == 1


# Export JSON tests

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
