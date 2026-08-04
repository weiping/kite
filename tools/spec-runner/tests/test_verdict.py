"""Verdict 五态的序列化与取值。"""
from spec_runner.verdict import Verdict


def test_五个判定值齐全():
    names = {v.name for v in Verdict}
    assert names == {"PASS", "FAIL", "SKIP", "UNCERTAIN", "PENDING_REVIEW"}


def test_序列化为小写无下划线():
    # 方案明确：pendingreview 不能写成 pending_review，否则下游静默忽略。
    assert Verdict.PENDING_REVIEW.value == "pendingreview"
    assert str(Verdict.PENDING_REVIEW) == "pendingreview"
    assert Verdict.PASS.value == "pass"
    assert Verdict.FAIL.value == "fail"
    assert Verdict.SKIP.value == "skip"
    assert Verdict.UNCERTAIN.value == "uncertain"


def test_可作字符串直接比较():
    assert Verdict.FAIL == "fail"
    assert Verdict.SKIP != "pass"
