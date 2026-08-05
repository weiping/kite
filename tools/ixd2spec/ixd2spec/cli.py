"""ixd2spec 命令行：解析页面规约，打印 golden 场景，并对缺失的标准状态告警。"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ixd2spec.page import parse_page, to_scenarios


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ixd2spec",
                                    description="页面规约状态流转 → 契约 golden 测试义务")
    parser.add_argument("page", help="docs/ixd/pages/<page>.md")
    parser.add_argument("--lib", help="对应实现路径，缺省由文件名推导")
    parser.add_argument("--dart-test-dir", default="apps/mobile/test")
    args = parser.parse_args(argv)

    page_path = Path(args.page)
    page = parse_page(page_path.read_text(encoding="utf-8"))

    missing = page.missing_standard()
    if missing:
        print(f"[warn] {page.name} 缺失标准状态: {', '.join(missing)}", file=sys.stderr)

    lib = args.lib or f"apps/mobile/lib/{page_path.stem.replace('-', '_')}.dart"
    for block in to_scenarios(page, args.dart_test_dir, lib):
        print(block)
        print()
    return 0
