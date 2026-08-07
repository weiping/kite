"""退出码到五态的映射。严格对照方案「退出码到五态的映射」那张表。"""
from spec_runner.adapters import ADAPTERS
from spec_runner.adapters.base import ExecResult
from spec_runner.verdict import Verdict

pytest = ADAPTERS["py"]
flutter = ADAPTERS["dart"]
semgrep = ADAPTERS["semgrep"]


# ---- pytest -------------------------------------------------------------
def test_pytest_退出0_收集大于0_是pass():
    r = ExecResult(exit_code=0, stdout="collected 3 items", collected=3)
    assert pytest.classify(r)[0] is Verdict.PASS


def test_pytest_退出0_收集为0_是fail_契约缺陷():
    # 选择器命中零个测试 = 契约缺陷，不能算通过
    r = ExecResult(exit_code=0, stdout="collected 0 items", collected=0)
    v, why = pytest.classify(r)
    assert v is Verdict.FAIL
    assert "零个测试" in why


def test_pytest_退出1_是fail():
    assert pytest.classify(ExecResult(1, "1 failed"))[0] is Verdict.FAIL


def test_pytest_未安装判uncertain_工具缺失():
    # python -m pytest 未装时 exit 1 + No module named，应判工具缺失而非测试失败
    v, why = pytest.classify(ExecResult(1, stderr="No module named pytest"))
    assert v is Verdict.UNCERTAIN


def test_pytest_退出5_未收集到测试_是fail():
    assert pytest.classify(ExecResult(5, "no tests ran"))[0] is Verdict.FAIL


def test_pytest_退出4_含未找到标记_是fail_悬空选择器():
    r = ExecResult(4, stdout="ERROR: not found: test_x.py::test_y")
    v, why = pytest.classify(r)
    assert v is Verdict.FAIL
    assert "悬空" in why


def test_pytest_退出4_其余_是uncertain_工具链问题():
    v, _ = pytest.classify(ExecResult(4, stdout="usage error: bad option"))
    assert v is Verdict.UNCERTAIN


def test_pytest_退出2或3_是uncertain():
    assert pytest.classify(ExecResult(2, ""))[0] is Verdict.UNCERTAIN
    assert pytest.classify(ExecResult(3, ""))[0] is Verdict.UNCERTAIN


def test_pytest_从stdout解析收集数():
    # 不传 collected 时应从 "collected N items" 解析
    v, why = pytest.classify(ExecResult(0, stdout="collected 5 items\n5 passed"))
    assert v is Verdict.PASS
    assert "5" in why


# ---- flutter ------------------------------------------------------------
def test_flutter_可见测试为0_是fail():
    v, why = flutter.classify(ExecResult(0, "", collected=0))
    assert v is Verdict.FAIL
    assert "可见测试数为 0" in why or "零个" in why


def test_flutter_有非成功结果_是fail():
    assert flutter.classify(ExecResult(1, "", collected=3))[0] is Verdict.FAIL


def test_flutter_命令不存在_是uncertain_不等于被证伪():
    r = ExecResult(127, stderr="flutter: command not found")
    assert flutter.classify(r)[0] is Verdict.UNCERTAIN


def test_flutter_从输出解析可见测试数():
    # flutter test 默认输出 "+N: ..."；无 collected 时应从中解析 visible
    out = "00:00 +1: test_a\n00:00 +2: All tests passed!\n"
    v, why = flutter.classify(ExecResult(0, out))
    assert v is Verdict.PASS
    assert "2" in why


# ---- semgrep ------------------------------------------------------------
def test_semgrep_退出0_无发现_是pass():
    assert semgrep.classify(ExecResult(0, ""))[0] is Verdict.PASS


def test_semgrep_退出1_有发现_是fail_违反不变量():
    assert semgrep.classify(ExecResult(1, "ran 1 rule"))[0] is Verdict.FAIL


def test_semgrep_退出2_规则文件错误_是uncertain():
    assert semgrep.classify(ExecResult(2, ""))[0] is Verdict.UNCERTAIN
