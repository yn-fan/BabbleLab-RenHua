"""Check that a standalone installation keeps provenance and can run offline."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "babblelab-renhua"


class DistributionTest(unittest.TestCase):
    def test_upstream_bundled_files_match_locked_hashes(self):
        lock = json.loads((SKILL / "sources.lock.json").read_text(encoding="utf-8"))
        bundled = []
        for source in lock["upstreams"]:
            self.assertRegex(source["revision"], r"^[0-9a-f]{40}$")
            for entry in source["files"]:
                if "bundled_path" in entry:
                    path = SKILL / entry["bundled_path"]
                    self.assertTrue(path.resolve().is_relative_to(SKILL.resolve()))
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])
                    bundled.append(path)
        self.assertEqual(len(bundled), 3)

    def test_package_has_notices_and_resolvable_document_links(self):
        self.assertEqual((ROOT / "LICENSE").read_bytes(), (SKILL / "LICENSE").read_bytes())
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts:
                continue
            # Only Markdown destinations are checked; shell examples are not links.
            for target in re.findall(r"\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
                if "://" in target or target.startswith("#"):
                    continue
                self.assertTrue((path.parent / target.split("#")[0]).exists(), f"{path}: {target}")

    def test_install_is_portable_and_cannot_overwrite_existing_install(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary) / "个人 技能"
            command = [sys.executable, str(ROOT / "tools" / "install.py"), "--to", str(parent)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            installed = parent / "babblelab-renhua"
            for source in SKILL.rglob("*"):
                if source.is_file() and "__pycache__" not in source.parts:
                    self.assertEqual(source.read_bytes(), (installed / source.relative_to(SKILL)).read_bytes())
            source_doc = Path(temporary) / "原稿.md"
            source_doc.write_text("核心是：试用期为三个月，可能延长。", encoding="utf-8")
            result = subprocess.run([sys.executable, str(installed / "scripts" / "renhua.py"),
                                     "analyze", str(source_doc), "--json"],
                                    capture_output=True, text=True, cwd=temporary)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("raw", json.loads(result.stdout))
            sentinel = installed / "local-note.txt"
            sentinel.write_text("keep me", encoding="utf-8")
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(), "keep me")

    def test_install_refuses_existing_symlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            (parent / "babblelab-renhua").symlink_to(parent / "missing")
            result = subprocess.run([sys.executable, str(ROOT / "tools" / "install.py"),
                                     "--to", str(parent)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((parent / "missing").exists())

    def test_install_refuses_recursion_into_source_tree(self):
        parent = SKILL / "recursive-install-test"
        self.assertFalse(parent.exists())
        result = subprocess.run([sys.executable, str(ROOT / "tools" / "install.py"),
                                 "--to", str(parent)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(parent.exists())


if __name__ == "__main__":
    unittest.main()
