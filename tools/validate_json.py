#!/usr/bin/env python3
import json
import sys
from pathlib import Path

import jsonschema


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 tools/validate_json.py <schema.json> <data.json>")
        return 2

    schema_path = Path(sys.argv[1])
    data_path = Path(sys.argv[2])

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        data = json.loads(data_path.read_text(encoding="utf-8"))
        jsonschema.validate(instance=data, schema=schema)
    except FileNotFoundError as exc:
        print(f"ERROR: file not found: {exc.filename}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {data_path}: {exc}")
        return 1
    except jsonschema.ValidationError as exc:
        path = ".".join(str(p) for p in exc.absolute_path) or "<root>"
        print(f"ERROR: schema validation failed at {path}: {exc.message}")
        return 1

    print(f"OK: {data_path} matches {schema_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
