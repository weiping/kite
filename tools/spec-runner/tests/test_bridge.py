"""bridge: make_decisions 把 spec-runner 结果转成 agent-spec resolve-ai 的 decisions。"""
from spec_runner.bridge import make_decisions
from spec_runner.runner import ScenarioResult
from spec_runner.verdict import Verdict


def test_make_decisions_生成agent_spec格式():
    results = [
        ScenarioResult("场景A", "py", "tests/a::t", Verdict.PASS, "pytest 退出 0"),
        ScenarioResult("场景B", "py", "tests/b::t", Verdict.FAIL, "断言失败"),
    ]
    decisions = make_decisions(results)
    assert decisions[0] == {
        "scenario_name": "场景A",
        "verdict": "pass",
        "reasoning": "pytest 退出 0",
        "model": "spec-runner",
        "confidence": 1.0,
    }
    assert decisions[1]["verdict"] == "fail"
    assert decisions[1]["confidence"] == 0.0


def test_make_decisions_字段顺序与resolve_ai要求一致():
    # resolve-ai 要求数组，每项含 scenario_name/verdict/reasoning/model/confidence
    d = make_decisions([ScenarioResult("s", "py", "f", Verdict.PASS, "r")])[0]
    assert set(d.keys()) == {"scenario_name", "verdict", "reasoning", "model", "confidence"}
