"""dtcg2flutter：DTCG 令牌 → Flutter 主题 Dart 代码。"""
import json

from dtcg2flutter.tokens import parse_tokens
from dtcg2flutter.render import render_dart, to_color, to_dimension

DTCG = {
    "color": {
        "primary": {"$value": "#3b82f6", "$type": "color"},
        "surface": {"$value": "#ffffff", "$type": "color"},
        "brand": {"$value": "#f80", "$type": "color"},
    },
    "space": {
        "md": {"$value": "16px", "$type": "dimension"},
        "lg": {"$value": "24px", "$type": "dimension"},
    },
}


def test_parse_tokens_展平DTCG树():
    tokens = parse_tokens(DTCG)
    paths = {t.path for t in tokens}
    assert ("color", "primary") in paths
    assert ("space", "md") in paths
    assert len(tokens) == 5
    by_path = {t.path: t for t in tokens}
    assert by_path[("color", "primary")].type == "color"
    assert by_path[("space", "md")].value == "16px"


def test_parse_tokens_忽略顶层schema元数据():
    tokens = parse_tokens({"$schema": "x", "color": {"x": {"$value": "#000", "$type": "color"}}})
    assert len(tokens) == 1


def test_to_color_六位十六进制():
    assert to_color("#3b82f6") == "Color(0xFF3B82F6)"


def test_to_color_三位简写展开():
    assert to_color("#f80") == "Color(0xFFFF8800)"


def test_to_dimension_去掉px转浮点():
    assert to_dimension("16px") == "16.0"
    assert to_dimension("24") == "24.0"


def test_render_dart_按类型分组到类():
    dart = render_dart(parse_tokens(DTCG))
    assert "class AppColors" in dart
    assert "class AppSpacing" in dart
    assert "static const primary = Color(0xFF3B82F6);" in dart
    assert "static const md = 16.0;" in dart
    assert "import 'package:flutter/material.dart';" in dart


def test_render_dart_无某类型则不生成该类():
    dart = render_dart(parse_tokens({"color": {"x": {"$value": "#000", "$type": "color"}}}))
    assert "AppColors" in dart
    assert "AppSpacing" not in dart
