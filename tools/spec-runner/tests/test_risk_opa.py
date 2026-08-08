"""opa 集成测试：真跑 risk.rego。本地无 opa 自动跳过，CI（setup-opa）跑。"""
from __future__ import annotations

import shutil

import pytest

from spec_runner import risk

POLICY = risk.POLICY_DIR / "risk.rego"


@pytest.mark.skipif(shutil.which("opa") is None, reason="无 opa，CI 跑")
def test_R3改policy目录():
    """改 policy/ 下文件 → R3（最严档）。"""
    out = risk.evaluate_risk(
        {"changed_files": ["policy/risk.rego"], "changed_lines": 1,
         "dangling_selectors": [], "boundary_violations": 0}, policy=POLICY)
    assert out["level"] == "R3"


@pytest.mark.skipif(shutil.which("opa") is None, reason="无 opa，CI 跑")
def test_R0小改动文案():
    """小改动非敏感路径 → R0（自动放行）。"""
    out = risk.evaluate_risk(
        {"changed_files": ["docs/readme.md"], "changed_lines": 2,
         "dangling_selectors": [], "boundary_violations": 0}, policy=POLICY)
    assert out["level"] == "R0"


@pytest.mark.skipif(shutil.which("opa") is None, reason="无 opa，CI 跑")
def test_R1超50行():
    """常规路径超 50 行 → R1。"""
    out = risk.evaluate_risk(
        {"changed_files": ["services/a.py"], "changed_lines": 60,
         "dangling_selectors": [], "boundary_violations": 0}, policy=POLICY)
    assert out["level"] == "R1"


@pytest.mark.skipif(shutil.which("opa") is None, reason="无 opa，CI 跑")
def test_deny悬空选择器():
    """dangling_selectors 非空 → deny 非空。"""
    out = risk.evaluate_risk(
        {"changed_files": ["docs/x.md"], "changed_lines": 1,
         "dangling_selectors": ["不存在的选择器"], "boundary_violations": 0}, policy=POLICY)
    assert out["deny"], "deny 应非空"
