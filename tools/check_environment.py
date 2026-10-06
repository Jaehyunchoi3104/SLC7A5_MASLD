#!/usr/bin/env python3
"""Report installed Python distribution versions without importing analysis libraries."""
import argparse
from datetime import date
from importlib.metadata import PackageNotFoundError, version
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    packages = json.loads((ROOT / "environment/python-packages.json").read_text())
    observed = {}
    for name in packages:
        try:
            observed[name] = version(name)
        except PackageNotFoundError:
            observed[name] = None
    result = {"recorded_on": str(date.today()), "python": platform.python_version(),
              "platform": platform.system(), "packages": observed,
              "missing": [name for name, value in observed.items() if value is None],
              "scope": "Installed package metadata only; not an import, dependency solver or complete analysis test."}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Python {result['python']} ({result['platform']})")
        for name, value in observed.items():
            print(f"{name:20} {value or 'MISSING'}")
    return 1 if result["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
