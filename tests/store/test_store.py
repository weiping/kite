"""ItemStore 契约测试：跨实例持久、不丢失、可导出 JSON。"""
import json
import tempfile
from pathlib import Path

from hypothesis import given, strategies as st

from services.capture.classify import Item
from services.store.store import ItemStore


def test_persist_across_instances(tmp_path):
    """add 后新建 store(同 path) 仍能读到。"""
    store = ItemStore(tmp_path / "items.json")
    store.add(Item("task", "买牛奶", "明天要买牛奶"))
    # 新实例（模拟跨会话）
    store2 = ItemStore(tmp_path / "items.json")
    items = store2.list()
    assert len(items) == 1
    assert items[0].title == "买牛奶"


@given(n=st.integers(min_value=0, max_value=10))
def test_multiple_add_no_loss(n):
    """多次 add，list 返回全部、顺序保留。"""
    with tempfile.TemporaryDirectory() as d:
        store = ItemStore(Path(d) / "items.json")
        for i in range(n):
            store.add(Item("note", f"标题{i}", f"内容{i}"))
        items = store.list()
        assert len(items) == n
        assert [it.title for it in items] == [f"标题{i}" for i in range(n)]


def test_export_readable_json(tmp_path):
    """存储文件是合法 JSON、含 item 字段。"""
    path = tmp_path / "items.json"
    store = ItemStore(path)
    store.add(Item("event", "开会", "明天开会"))
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert data[0]["kind"] == "event"
    assert data[0]["title"] == "开会"
    assert "text" in data[0]


def test_corrupt_file_falls_back_to_empty(tmp_path):
    """文件损坏 → 读空，不崩。"""
    path = tmp_path / "items.json"
    path.write_text("{ 不是合法 json", encoding="utf-8")
    assert ItemStore(path).list() == []
