import json
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from slc7a5_paths import ProjectPaths


class PathTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "repo"
        (self.repo / "config").mkdir(parents=True)
        (self.repo / "config/paths.json").write_text(json.dumps({"data_root": "data", "seed": 42, "input_overrides": {}}))
        (self.repo / "config/inputs.json").write_text(json.dumps({"example": {"path": "cohort/value.txt", "generated": True}}))
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)

    def input_file(self):
        source = self.repo / "data/cohort/value.txt"
        source.parent.mkdir(parents=True)
        source.write_text("original")
        return source

    def test_output_and_input_with_same_name_are_separate(self):
        original = self.input_file()
        paths = ProjectPaths(self.repo)
        target = Path(paths.output("cohort/value.txt"))
        target.write_text("new result")
        self.assertEqual(original.read_text(), "original")
        self.assertNotEqual(paths.input("cohort/value.txt"), str(target))
        self.assertEqual(paths.dataset("example"), str(target))

    def test_explicit_override_takes_precedence_over_generated_file(self):
        original = self.input_file()
        (self.repo / "config/paths.local.json").write_text(json.dumps({"input_overrides": {"example": str(original)}}))
        paths = ProjectPaths(self.repo)
        Path(paths.output("cohort/value.txt")).write_text("generated")
        self.assertEqual(paths.dataset("example"), str(original))

    def test_environment_data_root_is_read_only(self):
        external = Path(self.temp.name) / "external"
        (external / "cohort").mkdir(parents=True)
        (external / "cohort/value.txt").write_text("external input")
        with patch.dict(os.environ, {"SLC7A5_DATA_ROOT": str(external)}):
            paths = ProjectPaths(self.repo)
        self.assertEqual(Path(paths.dataset("example")).read_text(), "external input")
        self.assertFalse((self.repo / "results").exists())

    def test_missing_input_does_not_create_directories(self):
        paths = ProjectPaths(self.repo)
        with self.assertRaises(FileNotFoundError):
            paths.dataset("example")
        self.assertFalse((self.repo / "data").exists())
        self.assertFalse((self.repo / "results").exists())

    def test_path_traversal_and_absolute_output_are_rejected(self):
        paths = ProjectPaths(self.repo)
        for bad in ["../outside.txt", "/tmp/outside.txt", "a/../../outside.txt", ""]:
            with self.subTest(path=bad), self.assertRaises(ValueError):
                paths.output(bad)

    def test_output_directory_symlink_cannot_escape(self):
        external = Path(self.temp.name) / "external"
        external.mkdir()
        (self.repo / "results").mkdir()
        (self.repo / "results/link").symlink_to(external, target_is_directory=True)
        paths = ProjectPaths(self.repo)
        with self.assertRaises(ValueError):
            paths.output("link/new/sub/file.txt")
        self.assertFalse((external / "new").exists())

    def test_existing_output_file_symlink_cannot_overwrite_input(self):
        original = self.input_file()
        (self.repo / "results").mkdir()
        (self.repo / "results/result.txt").symlink_to(original)
        with self.assertRaises(ValueError):
            ProjectPaths(self.repo).output("result.txt")
        self.assertEqual(original.read_text(), "original")

    def test_results_root_symlink_cannot_escape(self):
        external = Path(self.temp.name) / "external"
        external.mkdir()
        (self.repo / "results").symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            ProjectPaths(self.repo)

    def test_results_root_cannot_alias_input_directory_inside_repo(self):
        original = self.input_file()
        (self.repo / "results").symlink_to(self.repo / "data", target_is_directory=True)
        with self.assertRaises(ValueError):
            ProjectPaths(self.repo)
        self.assertEqual(original.read_text(), "original")

    def test_unknown_override_is_not_silently_ignored(self):
        (self.repo / "config/paths.local.json").write_text('{"input_overrides": {"typo": "x"}}')
        with self.assertRaises(ValueError):
            ProjectPaths(self.repo)


if __name__ == "__main__":
    unittest.main()
