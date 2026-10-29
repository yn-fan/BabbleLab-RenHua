#!/usr/bin/env python3
"""Copy the complete skill to a chosen skill directory without overwriting it."""

import argparse
from pathlib import Path
import shutil
import sys

NAME = "babblelab-renhua"
SOURCE = Path(__file__).resolve().parents[1] / "skills" / NAME


def install(parent):
    parent = Path(parent).expanduser().resolve()
    target = parent / NAME
    if target.is_relative_to(SOURCE.resolve()):
        raise ValueError("安装目录不能放在技能源目录内部。")
    # Reserve the final directory exclusively; even an existing symlink is refused.
    parent.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    try:
        shutil.copytree(SOURCE, target, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    except Exception:
        # This directory was created by this invocation, never an existing install.
        shutil.rmtree(target)
        raise
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description="安装 BabbleLab-RenHua 完整技能；已有同名目录时停止。")
    parser.add_argument("--to", required=True, help="技能父目录，例如 ~/.agents/skills")
    args = parser.parse_args(argv)
    try:
        target = install(args.to)
    except (OSError, ValueError) as error:
        parser.exit(2, f"安装未完成：{error}\n已有技能不会覆盖；请选择新的父目录。\n")
    print(f"已安装：{target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
