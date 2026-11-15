"""Unit tests for Lazy OS contract schemas and validator CLI."""

import json
from pathlib import Path
import pytest
import yaml

from lazy.common.contracts import (
    CONTRACT_SCHEMAS,
    ContractValidationError,
    load_payload,
    load_schema,
    validate_contract,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONTRACTS_DIR = REPO_ROOT / "docs" / "contracts"
VALID_DIR = REPO_ROOT / "tests" / "fixtures" / "contracts" / "valid"
INVALID_DIR = REPO_ROOT / "tests" / "fixtures" / "contracts" / "invalid"


def test_all_contract_schemas_exist_and_load():
    """Verify that all defined schemas exist in docs/contracts/ and are valid JSON."""
    for schema_type in CONTRACT_SCHEMAS:
        schema = load_schema(schema_type)
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "title" in schema


def test_valid_samples_pass_validation():
    """Verify that all 31 valid fixture samples pass schema validation."""
    valid_files = list(VALID_DIR.glob("valid_*.*"))
    assert len(valid_files) >= 30, f"Expected >=30 valid samples, found {len(valid_files)}"

    for file_path in valid_files:
        payload = load_payload(file_path)
        # Determine schema type from filename: valid_<type>_xx.json
        parts = file_path.stem.split("_")
        schema_type = parts[1]
        if schema_type == "manifest":
            schema_type = "capability_manifest"
        elif schema_type == "outbox":
            schema_type = "outbox_item"

        is_valid, err = validate_contract(schema_type, payload)
        assert is_valid, f"Expected {file_path.name} to be valid under {schema_type}, failed: {err}"
        assert err is None


def test_invalid_samples_fail_validation():
    """Verify that all 31 invalid fixture samples fail schema validation."""
    manifest_file = INVALID_DIR / "manifest.json"
    assert manifest_file.is_file()
    invalid_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert len(invalid_manifest) >= 30, f"Expected >=30 invalid samples, found {len(invalid_manifest)}"

    for item in invalid_manifest:
        file_path = INVALID_DIR / item["filename"]
        schema_type = item["expected_schema"]
        payload = load_payload(file_path)

        is_valid, err = validate_contract(schema_type, payload)
        assert not is_valid, f"Expected {file_path.name} to be invalid under {schema_type}, but passed!"
        assert err is not None
        assert len(err) > 0


def test_strict_mode_raises_exception():
    """Verify that strict=True raises ContractValidationError on invalid payload."""
    invalid_intent_file = INVALID_DIR / "invalid_intent_01.json"
    payload = load_payload(invalid_intent_file)

    with pytest.raises(ContractValidationError) as exc_info:
        validate_contract("intent", payload, strict=True)
    assert "Validation failed for intent" in str(exc_info.value)


def test_unknown_schema_type_raises():
    """Verify that unknown schema type raises ValueError."""
    with pytest.raises(ValueError):
        validate_contract("non_existent_type", {})


def test_cli_validator(monkeypatch, capsys):
    """Verify CLI tool execution for valid and invalid samples."""
    from lazy.common.contracts import main

    # 1. Valid sample CLI call
    valid_file = VALID_DIR / "valid_intent_01.json"
    monkeypatch.setattr("sys.argv", ["contracts.py", "validate", "intent", str(valid_file)])
    ret = main()
    assert ret == 0
    captured = capsys.readouterr()
    assert "VALID:" in captured.out

    # 2. Invalid sample CLI call
    invalid_file = INVALID_DIR / "invalid_intent_01.json"
    monkeypatch.setattr("sys.argv", ["contracts.py", "validate", "intent", str(invalid_file)])
    ret = main()
    assert ret == 1
    captured = capsys.readouterr()
    assert "INVALID:" in captured.err
