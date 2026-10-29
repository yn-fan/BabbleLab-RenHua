#!/usr/bin/env python3
"""Local text inspection and comparison; no model calls and no automatic rewrite."""

import argparse
import difflib
import html
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

NOTICE = "候选不是错误，也不是 AI 生成概率；每处修改都需要结合语境复核。"
BOUNDARY = (
    "上游规则只做启发式粗筛：引文、标题、列表、行内代码、元数据和部分代码围栏"
    "可能仍被计入；标点与字数统计包含全文。请保留这些位置的正常表达。"
)
COMPARISON_NOTICE = "指标减少不代表文稿更好；请另行核对事实、限定词、引用和作者语气。"


def load_detector():
    path = Path(__file__).parent / "vendor" / "lieflat" / "detect.py"
    spec = importlib.util.spec_from_file_location("renhua_lieflat_detect", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_document(value):
    path = Path(value)
    if path.suffix.lower() not in {".md", ".txt"}:
        raise ValueError(f"只接受 .md 或 .txt 文件：{path}")
    if not path.is_file():
        raise ValueError(f"找不到普通文本文件：{path}")
    text = path.read_text(encoding="utf-8-sig")
    if not text.strip():
        raise ValueError(f"文件为空：{path}")
    return path, text


def warnings_for(han):
    warnings = [NOTICE, BOUNDARY]
    if han == 0:
        warnings.append("没有汉字：中文统计不适用；请使用英语编辑规则人工审阅。")
    elif han < 500:
        warnings.append("少于 500 汉字：样本不足，密度与结构统计不宜推断整体风格；仍可复核局部候选。")
    warnings.append("统计引擎沿用 lieflat 的启发式规则；本工具未独立复核其研究结论。")
    return warnings


def analyze(detector, path, text):
    docs = [(path.name, text)]
    han = detector.hanzi(text)
    return {
        "schema": "babblelab-renhua.analysis.v1",
        "source": path.name,
        "han_characters": han,
        "chinese_statistics_applicable": han > 0,
        "warnings": warnings_for(han),
        "raw": detector.measure_docs(docs),
        "semantic_candidate_counts": detector.extract_candidates(docs)["meta"],
    }


def md_cell(value):
    return html.escape(str(value)).replace("|", "&#124;").replace("\n", " ")


def render_analysis(data, detector):
    out = ["# BabbleLab-RenHua 文稿检查", "", f"文件：{md_cell(data['source'])}", "",
           f"汉字：{data['han_characters']}。", ""]
    out.extend(f"> {warning}\n" for warning in data["warnings"])
    if not data["chinese_statistics_applicable"]:
        return "\n".join(out)
    raw = data["raw"]
    levels = {name: level for level, name, *_ in detector.REGEX_HITS}
    out += ["## 局部候选", "", "下表是原始命中数；X 为上游已排除项，H 需人审，其余也不自动删改。", "",
            "| 项目 | 类别 | 原始命中 |", "| --- | --- | ---: |"]
    for name, hits in raw["hits"].items():
        out.append(f"| {md_cell(name)} | {levels[name]} | {len(hits)} |")
    out += [f"| 同义词轮换粗筛 | B | {len(raw['syn_hits'])} |", "",
            "每项最多展示 3 处；完整命中可用 `analyze --json` 保存。", ""]
    for name, hits in raw["hits"].items():
        for hit in hits[:3]:
            out.append(f"- {md_cell(name)}，第 {hit['line']} 行：{md_cell(hit['excerpt'])}")
    out += ["", "## 分布记录", "", "仅记录当前文本，不设目标值，不判断好坏。", "",
            "| 项目 | 当前值 |", "| --- | ---: |"]
    for name, value in raw["structure"].items():
        out.append(f"| {md_cell(name)} | {value if value is not None else '未提供（样本或引擎限制）'} |")
    out += ["", f"语义候选共 {data['semantic_candidate_counts']['n_candidates']} 条；"
            "用 `candidates` 导出并结合原文标注。"]
    return "\n".join(out)


def measurement_rows(before, after):
    def values(data):
        raw = data["raw"]
        result = {"汉字": data["han_characters"], "段数": raw["meta"]["段数"],
                  "小标题数": raw["meta"]["小标题数"]}
        result.update({f"原始命中 / {name}": len(hits) for name, hits in raw["hits"].items()})
        result.update({f"结构 / {name}": value for name, value in raw["structure"].items()})
        return result
    b, a = values(before), values(after)
    return [{"metric": name, "before": b[name], "after": a[name],
             "delta": round(a[name] - b[name], 3)
             if isinstance(b[name], (int, float)) and isinstance(a[name], (int, float)) else None}
            for name in b]


def compare_data(detector, before, after):
    bp, bt = before
    ap, at = after
    b = analyze(detector, bp, bt)
    a = analyze(detector, ap, at)
    # Keep line endings so the diff can show a missing final newline explicitly.
    diff_lines = []
    for line in difflib.unified_diff(bt.splitlines(keepends=True), at.splitlines(keepends=True),
                                     fromfile=bp.name, tofile=ap.name):
        diff_lines.append(line.rstrip("\r\n"))
        if not line.endswith(("\n", "\r")):
            diff_lines.append("\\ No newline at end of file")
    return {"schema": "babblelab-renhua.comparison.v1", "notice": COMPARISON_NOTICE,
            "before": b, "after": a, "metrics": measurement_rows(b, a),
            "diff": "\n".join(diff_lines)}


def render_comparison(data, format_name):
    rows = data["metrics"]
    warnings = [NOTICE, COMPARISON_NOTICE]
    for side in ("before", "after"):
        warnings.extend(f"{data[side]['source']}：{w}" for w in data[side]["warnings"][1:])
    def number(value):
        return "不适用" if value is None else str(value)
    if format_name == "html":
        esc = html.escape
        table = "".join("<tr>" + "".join(f"<td>{esc(number(row[key]))}</td>"
                         for key in ("metric", "before", "after", "delta")) + "</tr>" for row in rows)
        return ("<!doctype html>\n<html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
                "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
                "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'none'; style-src 'unsafe-inline'\">"
                "<title>BabbleLab-RenHua 前后对照</title><style>"
                "body{max-width:1000px;margin:40px auto;padding:0 20px;font:16px/1.6 sans-serif;color:#222}"
                "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ddd;padding:8px;text-align:left}"
                "pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f5f5;padding:20px}"
                "</style></head><body><h1>BabbleLab-RenHua 前后对照</h1>"
                + "".join(f"<p>{esc(w)}</p>" for w in warnings)
                + "<table><thead><tr><th>项目</th><th>改前</th><th>改后</th><th>差值</th></tr></thead><tbody>"
                + table + "</tbody></table><h2>逐行差异</h2><pre>"
                + esc(data["diff"] or "两份文本相同。") + "</pre></body></html>")
    out = ["# BabbleLab-RenHua 前后对照", ""]
    out.extend(f"> {md_cell(w)}\n" for w in warnings)
    out += ["| 项目 | 改前 | 改后 | 差值 |", "| --- | ---: | ---: | ---: |"]
    for row in rows:
        out.append("| " + " | ".join(md_cell(number(row[k])) for k in ("metric", "before", "after", "delta")) + " |")
    # Raw prose must never become active HTML, a Markdown link, or a code fence.
    out += ["", "## 逐行差异", "", "<pre>", html.escape(data["diff"] or "两份文本相同。"), "</pre>"]
    return "\n".join(out)


def write_result(payload, out, inputs):
    if out is None:
        print(payload)
        return
    target = Path(out)
    if target.resolve() in {path.resolve() for path in inputs}:
        raise ValueError("输出路径不能是输入文件。")
    # Exclusive creation also rejects existing symlinks, including dangling ones.
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(payload + "\n")
    print(f"已保存：{target}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description="BabbleLab-RenHua：本地文稿检查与前后对照，不自动改稿。")
    commands = parser.add_subparsers(dest="command", required=True)
    analysis = commands.add_parser("analyze", help="检查单篇中文文稿")
    analysis.add_argument("input")
    analysis.add_argument("--json", action="store_true", help="保留全部原始统计")
    candidates = commands.add_parser("candidates", help="导出待语义复核的候选 JSON")
    candidates.add_argument("input")
    comparison = commands.add_parser("compare", help="比较改前和改后文稿")
    comparison.add_argument("before")
    comparison.add_argument("after")
    comparison.add_argument("--format", choices=("md", "html", "json"), default="md")
    for command in (analysis, candidates, comparison):
        command.add_argument("--out", help="写入新文件；省略时输出到 stdout；已有文件不会覆盖")
    args = parser.parse_args(argv)
    try:
        detector = load_detector()
        if args.command == "compare":
            before, after = read_document(args.before), read_document(args.after)
            inputs = [before[0], after[0]]
            result = compare_data(detector, before, after)
            payload = (json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json"
                       else render_comparison(result, args.format))
        else:
            path, text = read_document(args.input)
            inputs = [path]
            if args.command == "candidates":
                result = detector.extract_candidates([(path.name, text)])
                result["warnings"] = warnings_for(detector.hanzi(text))
                result["annotation_help"] = (
                    "保留原始候选，在每条上追加 label、confidence、reason、disposition；"
                    "判据见 references/semantic-review.md。"
                )
                payload = json.dumps(result, ensure_ascii=False, indent=2)
            else:
                result = analyze(detector, path, text)
                payload = (json.dumps(result, ensure_ascii=False, indent=2) if args.json
                           else render_analysis(result, detector))
        write_result(payload, args.out, inputs)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(2, f"错误：{error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
