"""Behavioral checks for the CLI's read-only contract and report boundaries."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "skills" / "babblelab-renhua" / "scripts" / "renhua.py"


class CLITest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def document(self, name="原稿.md", text="核心是：试用期为三个月，可能延长。\n"):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def run_cli(self, *args, success=True):
        result = subprocess.run([sys.executable, str(CLI), *map(str, args)],
                                text=True, capture_output=True, cwd=self.root)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn("Traceback", result.stderr)
        return result

    def test_short_chinese_json_retains_candidates_and_exact_count(self):
        path = self.document()
        result = self.run_cli("analyze", path, "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["han_characters"], 14)
        self.assertEqual(len(data["raw"]["hits"]["提示语冒号"]), 1)
        self.assertTrue(any("少于 500" in w for w in data["warnings"]))
        self.assertTrue(any("不是 AI 生成概率" in w for w in data["warnings"]))
        self.assertEqual(result.stderr, "")

    def test_english_does_not_claim_applicable_chinese_statistics(self):
        path = self.document(text="The trial may last three months.\n")
        data = json.loads(self.run_cli("analyze", path, "--json").stdout)
        self.assertFalse(data["chinese_statistics_applicable"])
        self.assertTrue(any("中文统计不适用" in w for w in data["warnings"]))
        report = self.run_cli("analyze", path).stdout
        self.assertNotIn("局部候选", report)

    def test_quote_and_code_boundaries_are_disclosed(self):
        path = self.document(text='> 核心是：这是一句引文，不能改写。\n\n```text\n核心是：代码内容不改。\n```\n')
        data = json.loads(self.run_cli("analyze", path, "--json").stdout)
        hits = data["raw"]["hits"]["提示语冒号"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["line"], 1)
        self.assertTrue(any("引文" in w and "代码围栏" in w for w in data["warnings"]))

    def test_candidates_preserve_schema_and_support_annotation(self):
        path = self.document(text="核心是：团队已经完成本周的验收工作，剩余问题会在下次会议中逐项讨论并记录。\n")
        data = json.loads(self.run_cli("candidates", path).stdout)
        for key in ("meta", "rename", "cohesion", "colon", "iso3"):
            self.assertIn(key, data)
        self.assertTrue(data["colon"])
        self.assertIn("disposition", data["annotation_help"])
        self.assertEqual(data["colon"][0]["file"], "原稿.md")

    def test_html_report_escapes_text_and_file_names(self):
        before = self.document('<img src=x>.md', '<script>alert("before")</script>\n核心是：保留三个月。\n')
        after = self.document("改后.md", '<img src=x onerror=alert(1)>\n保留三个月。\n')
        html = self.run_cli("compare", before, after, "--format", "html").stdout
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img ", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img src=x&gt;.md", html)
        self.assertIn("default-src 'none'", html)
        self.assertIn("指标减少不代表", html)

    def test_compare_does_not_mutate_inputs(self):
        before = self.document()
        after = self.document("改后.txt", "试用期为三个月，可能延长。\n")
        snapshots = [before.read_bytes(), after.read_bytes()]
        data = json.loads(self.run_cli("compare", before, after, "--format", "json").stdout)
        hit = next(row for row in data["metrics"] if row["metric"] == "原始命中 / 提示语冒号")
        self.assertEqual((hit["before"], hit["after"], hit["delta"]), (1, 0, -1))
        self.assertIn("-核心是", data["diff"])
        self.assertEqual(snapshots, [before.read_bytes(), after.read_bytes()])

    def test_markdown_diff_cannot_inject_active_html(self):
        before = self.document(text="<script>alert(1)</script>\n```\n")
        after = self.document("改后.md", "<img src=x>\n```\n")
        report = self.run_cli("compare", before, after).stdout
        self.assertNotIn("<script>", report)
        self.assertNotIn("<img ", report)
        self.assertIn("&lt;script&gt;", report)

    def test_compare_records_missing_final_newline(self):
        before = self.document(text="原句。")
        after = self.document("改后.md", "原句。\n")
        data = json.loads(self.run_cli("compare", before, after, "--format", "json").stdout)
        self.assertIn("No newline at end of file", data["diff"])

    def test_new_output_is_valid_json_and_existing_output_is_preserved(self):
        path = self.document()
        output = self.root / "检查结果.json"
        result = self.run_cli("analyze", path, "--json", "--out", output)
        self.assertEqual(result.stdout, "")
        json.loads(output.read_text())
        previous = output.read_bytes()
        self.run_cli("analyze", path, "--json", "--out", output, success=False)
        self.assertEqual(output.read_bytes(), previous)

    def test_inputs_cannot_be_overwritten_even_by_alias(self):
        path = self.document()
        before = path.read_bytes()
        self.run_cli("analyze", path, "--out", path, success=False)
        alias = self.root / "alias.md"
        alias.symlink_to(path)
        self.run_cli("analyze", path, "--out", alias, success=False)
        hardlink = self.root / "hardlink.md"
        os.link(path, hardlink)
        self.run_cli("analyze", path, "--out", hardlink, success=False)
        self.assertEqual(path.read_bytes(), before)

    def test_dangling_output_symlink_is_not_followed(self):
        path = self.document()
        target = self.root / "new.json"
        output = self.root / "alias.json"
        output.symlink_to(target)
        self.run_cli("analyze", path, "--out", output, success=False)
        self.assertFalse(target.exists())

    def test_missing_empty_directory_binary_and_invalid_utf8_fail_cleanly(self):
        empty = self.document("empty.md", "  \n")
        unsupported = self.document("data.csv", "一,二\n")
        invalid = self.root / "bad.md"
        invalid.write_bytes(b"\xff\xfe\x00")
        directory = self.root / "directory.md"
        directory.mkdir()
        for path in (self.root / "missing.md", empty, unsupported, invalid, directory):
            with self.subTest(path=path):
                self.run_cli("analyze", path, success=False)


if __name__ == "__main__":
    unittest.main()
