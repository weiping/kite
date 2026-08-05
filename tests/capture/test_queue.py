"""离线队列契约测试：不丢失、不乱序（property）。"""
from hypothesis import given, strategies as st

from services.capture.queue import CaptureQueue


@given(seq=st.lists(st.text(min_size=1, max_size=10), max_size=20))
def test_offline_queue_preserves_order(seq):
    """离线捕获入队后逐条出队，顺序与入队一致且无丢失。"""
    q = CaptureQueue()
    for item in seq:
        q.enqueue(item)
    drained = q.drain()
    assert drained == seq
    assert q.drain() == []
