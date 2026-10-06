#!/usr/bin/env python3
"""Check required files without running analyses or reading expression matrices."""
import argparse
import csv
import json
import os
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from slc7a5_paths import ProjectPaths


def check_schema(path, key):
    issues = []
    details = {}
    if path.suffix == ".h5ad":
        try:
            import h5py
        except ImportError:
            return ["h5py is required for --schema on h5ad inputs"], details
        with h5py.File(path, "r") as f:
            for part in ("obs", "var", "X"):
                if part not in f:
                    issues.append(f"Missing AnnData component: {part}")
            for part in ("obs", "var"):
                if part in f:
                    index = f[part].attrs.get("_index", "_index")
                    if index in f[part]:
                        details[part + "_count"] = len(f[part][index])
    elif key in {"bulk_counts", "bulk_tpm", "hyu_metadata"}:
        delimiter = "\t" if path.suffix == ".tsv" else ","
        with path.open(encoding="utf-8-sig", newline="") as f:
            columns = next(csv.reader(f, delimiter=delimiter))
        if key.startswith("bulk_"):
            with (REPO / "config/bulk_samples.tsv").open() as f:
                expected = [r["sample"] for r in csv.DictReader(f, delimiter="\t")]
            if columns[:2] != ["gene_id", "gene_name"]:
                issues.append("Expected first columns: gene_id, gene_name")
            if sorted(columns[2:]) != sorted(expected):
                issues.append("Sample columns differ from config/bulk_samples.tsv")
            if len(set(columns[2:])) != len(columns[2:]):
                issues.append("Duplicate sample columns")
            details["sample_count"] = len(columns[2:])
        else:
            for column in ("Sample", "Disease", "Degree_of_fibrosis"):
                if column not in columns:
                    issues.append(f"Missing metadata column: {column}")
    return issues, details


def inspect_inputs(analyses, paths, selected, schema=False):
    rows = []
    for analysis in selected:
        entry = analyses[analysis]
        for optional, keys in [(False, entry["inputs"]), (True, entry.get("optional_inputs", []))]:
            for key in keys:
                path = Path(paths.dataset(key, required=False))
                exists = path.is_file()
                status = "present" if exists else "optional_missing" if optional else "missing"
                row = {"analysis": analysis, "input": key, "status": status,
                       "optional": optional, "path": str(path)}
                if exists:
                    row["bytes"] = path.stat().st_size
                    if schema:
                        try:
                            issues, details = check_schema(path, key)
                        except (OSError, ValueError, KeyError, StopIteration) as e:
                            issues, details = [str(e)], {}
                        row.update(details)
                        if issues:
                            row["status"] = "invalid"
                            row["issues"] = issues
                rows.append(row)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", action="append", help="Analysis ID; repeat to select several. Default: all")
    parser.add_argument("--data-root", help="Read existing inputs at this root; never copy them")
    parser.add_argument("--schema", action="store_true", help="Inspect headers/HDF5 structure without loading expression matrices")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.data_root:
        os.environ["SLC7A5_DATA_ROOT"] = args.data_root
    analyses = json.loads((REPO / "config/analyses.json").read_text())
    selected = list(analyses) if not args.analysis or args.analysis == ["all"] else args.analysis
    unknown = set(selected) - set(analyses)
    if unknown:
        parser.error(f"Unknown analyses: {sorted(unknown)}; choices: {', '.join(analyses)}")
    paths = ProjectPaths(REPO)
    rows = inspect_inputs(analyses, paths, selected, args.schema)
    bad = [r for r in rows if not r["optional"] and r["status"] != "present"]
    result = {"data_root": str(paths.data_root), "analyses_checked": len(selected),
              "required_failures": len(bad), "inputs": rows,
              "scope": "Input existence/selected schemas only; not a Figure reproduction test."}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for row in rows:
            print(f"{row['status']:17} {row['analysis']:20} {row['input']}")
            for issue in row.get("issues", []):
                print(f"  {issue}")
        print(f"Required input failures: {len(bad)}; analyses checked: {len(selected)}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
