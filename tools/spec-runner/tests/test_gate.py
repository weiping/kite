"""五态门禁：跳过永远阻断；不确定在 L2/L3 升级为人审级阻断。"""
from spec_runner.gate import gate
from spec_runner.verdict import Verdict


def R(scenario, verdict, reason=""):
    return {"scenario": scenario, "verdict": verdict, "reason": reason}


def test_全pass_放行():
    ok, problems = gate([R("a", Verdict.PASS), R("b", Verdict.PASS)], level="L1")
    assert ok is True and problems == []


def test_fail_阻断():
    ok, problems = gate([R("a", Verdict.FAIL, "断言失败")], level="L1")
    assert ok is False
    assert any("[fail]" in p for p in problems)


def test_skip_永远阻断_不设开关():
    # 跳过不等于通过——一旦提供跳过开关，某个赶工的周五会被打开再也关不掉。
    ok, problems = gate([R("a", Verdict.SKIP)], level="L1")
    assert ok is False
    assert "跳过不等于通过" in problems[0]


def test_pendingreview_阻断():
    ok, _ = gate([R("a", Verdict.PENDING_REVIEW)], level="L1")
    assert ok is False


def test_uncertain_在L1_升级人审():
    ok, problems = gate([R("a", Verdict.UNCERTAIN, "工具链缺失")], level="L1")
    assert ok is False
    assert "人审" in problems[0]


def test_uncertain_在L2_无人兜底():
    ok, problems = gate([R("a", Verdict.UNCERTAIN, "x")], level="L2")
    assert ok is False
    assert "无人兜底" in problems[0]


def test_uncertain_在L3_同样升级():
    ok, _ = gate([R("a", Verdict.UNCERTAIN, "x")], level="L3")
    assert ok is False
