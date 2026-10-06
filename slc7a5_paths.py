"""Portable input paths and repository-local outputs for the manuscript scripts.

This module uses only the Python standard library. Reading a path never stages,
copies or changes the input. New files are written below this repository's results/.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import sys


class ProjectPaths:
    def __init__(self, repo: str | Path | None = None):
        self.repo = Path(repo or Path(__file__).parent).resolve()
        self.config = json.loads((self.repo / "config/paths.json").read_text())
        local = self.repo / "config/paths.local.json"
        if local.exists():
            self.config.update(json.loads(local.read_text()))
        self.catalog = json.loads((self.repo / "config/inputs.json").read_text())
        value = os.environ.get("SLC7A5_DATA_ROOT") or self.config["data_root"]
        self.data_root = self._absolute(value)
        self.results_root = (self.repo / "results").resolve()
        if self.results_root != self.repo / "results":
            raise ValueError("results/ must be a real repository directory, not a symlink to another location.")
        self.overrides = self.config.get("input_overrides", {})
        unknown = set(self.overrides) - set(self.catalog)
        if unknown:
            raise ValueError(f"Unknown input override IDs: {sorted(unknown)}")
        self.by_path = {v["path"]: k for k, v in self.catalog.items()}

    def _absolute(self, value: str) -> Path:
        p = Path(value).expanduser()
        return (p if p.is_absolute() else self.repo / p).resolve()

    @staticmethod
    def _relative(value: str | Path) -> Path:
        p = Path(value)
        if p.is_absolute() or ".." in p.parts or not p.parts:
            raise ValueError(f"Expected a non-empty project-relative path: {value}")
        return p

    def input(self, relative: str, *, required: bool = True) -> str:
        rel = self._relative(relative)
        key = self.by_path.get(rel.as_posix())
        path = self._absolute(self.overrides[key]) if key in self.overrides else (self.data_root / rel).resolve()
        if required and not path.exists():
            raise FileNotFoundError(
                f"Missing input{f' [{key}]' if key else ''}: {path}\n"
                "Set SLC7A5_DATA_ROOT or config/paths.local.json; see docs/data_requirements.md."
            )
        return str(path)

    def output(self, relative: str, *, directory: bool = False, create: bool = True) -> str:
        rel = self._relative(relative)
        path = (self.results_root / rel).resolve()
        if not path.is_relative_to(self.results_root):
            raise ValueError(f"Output escapes results/: {relative}")
        if create:
            (path if directory else path.parent).mkdir(parents=True, exist_ok=True)
        return str(path) + (os.sep if directory else "")

    def artifact(self, relative: str, *, required: bool = True) -> str:
        """Use a freshly generated result, otherwise the supplied input snapshot."""
        generated = Path(self.output(relative, create=False))
        if generated.exists():
            return str(generated)
        return self.input(relative, required=required)

    def dataset(self, key: str, *, required: bool = True) -> str:
        entry = self.catalog[key]
        # An explicit override is authoritative, including for generated artifacts.
        if key in self.overrides:
            return self.input(entry["path"], required=required)
        resolver = self.artifact if entry.get("generated") else self.input
        return resolver(entry["path"], required=required)


_paths = None


def project_paths() -> ProjectPaths:
    global _paths
    if _paths is None:
        _paths = ProjectPaths()
    return _paths


def input_path(relative, *, required=True):
    return project_paths().input(relative, required=required)


def artifact_path(relative, *, required=True):
    paths = project_paths()
    key = paths.by_path.get(Path(relative).as_posix())
    if key in paths.overrides:
        return paths.input(relative, required=required)
    return paths.artifact(relative, required=required)


def dataset_path(key, *, required=True):
    return project_paths().dataset(key, required=required)


def output_path(relative):
    return project_paths().output(relative)


def output_dir(relative):
    return project_paths().output(relative, directory=True)


def setup_notebook(analysis_id):
    """Isolate relative saves and cache files; keep explicit per-analysis seeds."""
    paths = project_paths()
    workdir = paths.output(f"runs/{analysis_id}", directory=True)
    os.chdir(workdir)
    random.seed(paths.config["seed"])
    # Avoid importing large optional analysis dependencies in the path helper.
    if "numpy" in sys.modules:
        sys.modules["numpy"].random.seed(paths.config["seed"])
    return workdir
