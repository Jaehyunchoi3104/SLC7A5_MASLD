#!/usr/bin/env python3
"""Validate manuscript source syntax, notebook format and input references."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import argparse
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def validate(rscript=None):
    import nbformat
    analyses = json.loads((ROOT / "config/analyses.json").read_text())
    catalog = json.loads((ROOT / "config/inputs.json").read_text())
    issues = []
    counts = {"analyses": len(analyses), "notebooks": 0, "rmd": 0, "python": 0, "r_chunks": 0}
    for key, entry in analyses.items():
        path = ROOT / entry["script"]
        for name in entry["inputs"] + entry.get("optional_inputs", []):
            if name not in catalog:
                issues.append(f"{key}: unknown input {name}")
        if not path.is_file():
            issues.append(f"Missing script: {path}")
            continue
        if path.suffix == ".ipynb":
            counts["notebooks"] += 1
            doc = nbformat.read(path, as_version=4)
            try:
                nbformat.validate(doc)
            except Exception as e:
                issues.append(f"{entry['script']}: {e}")
            chunks = [(i, c.source) for i, c in enumerate(doc.cells) if c.cell_type == "code"]
            for i, cell in enumerate(doc.cells):
                if cell.cell_type == "code" and (cell.outputs or cell.execution_count is not None):
                    issues.append(f"{entry['script']} cell {i}: stored execution output")
        elif path.suffix == ".py":
            counts["python"] += 1
            chunks = [(0, path.read_text())]
        else:
            counts["rmd"] += 1
            labels = [m.group(1) for m in re.finditer(r"^```\{r\s+([A-Za-z][A-Za-z0-9_.-]*)(?=[,}])", path.read_text(), re.M)]
            repeated = sorted({label for label in labels if labels.count(label) > 1})
            if repeated:
                issues.append(f"{entry['script']}: repeated R chunk labels: {repeated}")
            chunks_r = re.findall(r"^```\{r[^\n]*\}\n(.*?)^```", path.read_text(), re.M | re.S)
            counts["r_chunks"] += len(chunks_r)
            if re.search(r"/home/|~/Liver_bio_project", "\n".join(chunks_r)):
                issues.append(f"{entry['script']}: fixed personal path")
            if rscript:
                with tempfile.TemporaryDirectory() as td:
                    p = Path(td) / "chunks.R"
                    p.write_text("\n\n".join(chunks_r))
                    result = subprocess.run([rscript, "--vanilla", "-e", "parse(file=commandArgs(TRUE)[1]);cat('PARSE_OK\\n')", str(p)], capture_output=True, text=True)
                if result.returncode:
                    issues.append(f"{entry['script']}: R parse error: {result.stderr[-1000:]}")
            continue
        for i, source in chunks:
            try:
                tree = ast.parse(source)
            except SyntaxError as e:
                issues.append(f"{entry['script']} cell {i}: {e}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith(("/home/", "//home/", "~/Liver_bio_project")):
                    issues.append(f"{entry['script']} cell {i}: fixed personal path")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dataset_path" and node.args and isinstance(node.args[0], ast.Constant):
                    if node.args[0].value not in catalog:
                        issues.append(f"{entry['script']} cell {i}: unknown dataset ID")
    helpers = sorted({name for entry in analyses.values() for name in entry.get("helpers", [])})
    counts["helpers"] = len(helpers)
    for name in helpers:
        path = ROOT / name
        if not path.is_file():
            issues.append(f"Missing helper: {name}")
            continue
        if path.suffix == ".py":
            try:
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith(("/home/", "/HL8/")):
                        issues.append(f"{name}: fixed personal path")
            except SyntaxError as e:
                issues.append(f"{name}: {e}")
        elif path.suffix == ".R" and rscript:
            result = subprocess.run([rscript, "--vanilla", "-e", "parse(file=commandArgs(TRUE)[1])", str(path)], capture_output=True, text=True)
            if result.returncode:
                issues.append(f"{name}: R parse error: {result.stderr[-1000:]}")
    return {"checks": counts, "issues": issues, "r_syntax_checked": bool(rscript),
            "scope": "Manuscript scripts only. Syntax/schema checks do not establish full runtime or scientific reproducibility."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rscript", help="Rscript executable for R Markdown syntax checks")
    parser.add_argument("--original-root", help="Also verify original source files against the initial copy manifest")
    args = parser.parse_args()
    result = validate(args.rscript)
    if args.original_root:
        with (ROOT / "docs/source_manifest.tsv").open() as f:
            originals = list(csv.DictReader(f, delimiter="\t"))
        # Preserve the initial manifest; later synchronization snapshots override its rows.
        current = {row["source_path"]: row for row in originals}
        updates = ROOT / "docs/update_source_manifest.tsv"
        if updates.is_file():
            with updates.open() as f:
                current.update({row["source_path"]: row for row in csv.DictReader(f, delimiter="\t")})
        originals = list(current.values())
        bad = []
        for row in originals:
            path = Path(args.original_root) / row["source_path"]
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row["source_sha256"]:
                bad.append(row["source_path"])
        result["originals_checked"] = len(originals)
        result["original_mismatches"] = bad
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["issues"] or result.get("original_mismatches") else 0


if __name__ == "__main__":
    raise SystemExit(main())
