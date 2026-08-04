"""离线通知存储隔离：两服务写不同库位，同一用户通知不被互相覆盖。

Level: property —— 差分式：同一序列打两个服务，比对各自库位完整性。
"""
from hypothesis import given, strategies as st

from services.api.notify import ApiNotify
from services.orchestrator.notify import OrchestratorNotify


@given(seq=st.lists(st.tuples(st.text(min_size=1, max_size=5), st.text(max_size=10)), max_size=20))
def test_two_services_do_not_overwrite(seq):
    storage: dict = {}
    orch = OrchestratorNotify(storage)
    api = ApiNotify(storage)
    for user, payload in seq:
        orch.store_notify(user, payload)
        api.store_notify(user, payload)
    # 去重保留最后写入；两服务按服务名分库位，各自独立、互不覆盖
    expected = {}
    for user, payload in seq:
        expected[user] = payload
    for user, payload in expected.items():
        assert storage[("orchestrator", user)] == payload
        assert storage[("api", user)] == payload
