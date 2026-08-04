"""dtcg2flutter 命令行：DTCG tokens.json → Flutter Dart 主题文件。"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dtcg2flutter.render import render_dart
from dtcg2flutter.tokens import parse_tokens


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dtcg2flutter",
                                    description="DTCG 设计令牌 → Flutter 主题 Dart")
    parser.add_argument("tokens", help="DTCG tokens.json")
    parser.add_argument("-o", "--out", default="packages/design/app_tokens.dart")
    args = parser.parse_args(argv)

    dtcg = json.loads(Path(args.tokens).read_text(encoding="utf-8"))
    dart = render_dart(parse_tokens(dtcg))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dart, encoding="utf-8")
    print(f"已生成 {out} ({len(dart.splitlines())} 行)")
    return 0
