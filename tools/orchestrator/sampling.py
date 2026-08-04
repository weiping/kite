# tools/orchestrator/sampling.py
# 确定性抽检：同一提交在同一周内结果恒定，且任何人可复算。
import hashlib
from datetime import date


def should_sample(commit_sha: str, rate: float = 0.20, salt: str = "") -> bool:
    """R1 抽检不能用随机数——随机意味着无法复算，一次争议就说不清。

    三个性质：
    - 可复算：任何人拿提交哈希都能算出同样结果
    - 周内稳定：重跑 CI 不会改变抽检结论，避免反复触发直到不被抽中
    - 跨周轮转：同一个长期分支不会永远逃过抽检
    """
    year, week, _ = date.today().isocalendar()
    key = f"{commit_sha}:{year}W{week:02d}:{salt}"
    digest = hashlib.sha256(key.encode()).hexdigest()
    return int(digest[:8], 16) / 0xFFFFFFFF < rate
