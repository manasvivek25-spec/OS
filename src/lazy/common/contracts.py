"""Contract validation module and CLI for Lazy OS contracts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import jsonschema
import yaml
import datetime

# Register ISO date-time checker using standard library datetime
@jsonschema.FormatChecker.cls_checks("date-time")
def _check_datetime_format(val: Any) -> bool:
    if not isinstance(val, str):
        return False
    try:
        s = val.replace("Z", "+00:00")
        datetime.datetime.fromisoformat(s)
        return True
    except Exception:
        return False

CONTRACT_SCHEMAS: Dict[str, str] = {
    "intent": "intent.schema.json",
    "plan": "plan.schema.json",
    "decision": "decision.schema.json",
    "event": "event.schema.json",
    "task": "task.schema.json",
    "outbox_item": "outbox_item.schema.json",
    "capability_manifest": "capability_manifest.schema.json",
}

_SCHEMA_CACHE: Dict[str, Dict[str, Any]] = {}
_STORE_CACHE: Optional[Dict[str, Any]] = None


class ContractValidationError(Exception):
    """Raised when a data payload fails contract schema validation."""


def get_contracts_dir() -> Path:
    """Find the docs/contracts directory relative to repo root or system share."""
    system_paths = [
        Path("/usr/share/lazy/contracts"),
        Path("/etc/lazy/contracts"),
    ]
    for sp in system_paths:
        if sp.is_dir():
            return sp

    candidate = Path(__file__).resolve().parent
    for _ in range(5):
        schema_path = candidate / "docs" / "contracts"
        if schema_path.is_dir():
            return schema_path
        candidate = candidate.parent
    raise FileNotFoundError("Could not locate docs/contracts directory")


def get_schema_store() -> Dict[str, Any]:
    """Build and cache an offline schema store for local $ref resolution."""
    global _STORE_CACHE
    if _STORE_CACHE is not None:
        return _STORE_CACHE

    store: Dict[str, Any] = {}
    contracts_dir = get_contracts_dir()
    for fname in CONTRACT_SCHEMAS.values():
        fpath = contracts_dir / fname
        if fpath.is_file():
            with open(fpath, "r", encoding="utf-8") as f:
                parsed = json.load(f)
                store[fname] = parsed
                store[fpath.as_uri()] = parsed
                if "$id" in parsed:
                    store[parsed["$id"]] = parsed
    _STORE_CACHE = store
    return store


def load_schema(schema_type: str) -> Dict[str, Any]:
    """Load and cache a contract JSON schema by type name."""
    type_key = schema_type.lower()
    if type_key not in CONTRACT_SCHEMAS:
        valid_types = ", ".join(CONTRACT_SCHEMAS.keys())
        raise ValueError(f"Unknown contract schema type '{schema_type}'. Valid types: {valid_types}")

    if type_key not in _SCHEMA_CACHE:
        schema_filename = CONTRACT_SCHEMAS[type_key]
        schema_file = get_contracts_dir() / schema_filename
        if not schema_file.is_file():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        with open(schema_file, "r", encoding="utf-8") as f:
            _SCHEMA_CACHE[type_key] = json.load(f)

    return _SCHEMA_CACHE[type_key]


def validate_contract(schema_type: str, data: Any, strict: bool = False) -> Tuple[bool, Optional[str]]:
    """Validate data dictionary against the designated contract schema.

    Returns (is_valid, error_message). If strict=True, raises ContractValidationError on failure.
    """
    # Let ValueError propagate for invalid schema type
    schema = load_schema(schema_type)
    contracts_dir = get_contracts_dir()
    store = get_schema_store()

    try:
        schema_path_uri = contracts_dir.as_uri() + "/"
        resolver = jsonschema.RefResolver(base_uri=schema_path_uri, referrer=schema, store=store)
        format_checker = jsonschema.FormatChecker()

        validator_cls = jsonschema.validators.validator_for(schema)
        validator = validator_cls(schema, resolver=resolver, format_checker=format_checker)
        validator.validate(data)
        return True, None
    except jsonschema.ValidationError as err:
        msg = f"Validation failed for {schema_type}: {err.message} (path: {'/'.join(str(p) for p in err.path)})"
        if strict:
            raise ContractValidationError(msg) from err
        return False, msg
    except Exception as err:
        msg = f"Contract error for {schema_type}: {str(err)}"
        if strict:
            raise ContractValidationError(msg) from err
        return False, msg


def load_payload(file_path: Path | str) -> Any:
    """Load JSON or YAML payload from file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    content = path.read_text(encoding="utf-8")
    if path.suffix in [".yaml", ".yml"]:
        return yaml.safe_load(content)
    return json.loads(content)


def main() -> int:
    """CLI validator entrypoint."""
    parser = argparse.ArgumentParser(description="Lazy OS Contract Validator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    val_parser = subparsers.add_parser("validate", help="Validate a JSON or YAML file against a contract schema")
    val_parser.add_argument("schema_type", choices=list(CONTRACT_SCHEMAS.keys()), help="Contract schema type")
    val_parser.add_argument("file_path", type=Path, help="Path to JSON or YAML file")

    args = parser.parse_args()

    if args.command == "validate":
        try:
            payload = load_payload(args.file_path)
            valid, err = validate_contract(args.schema_type, payload)
            if valid:
                print(f"VALID: {args.file_path} matches schema '{args.schema_type}'")
                return 0
            else:
                print(f"INVALID: {err}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
