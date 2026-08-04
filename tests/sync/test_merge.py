"""离线笔记冲突合并的契约测试。

Level: property 的场景真的遍历输入空间（hypothesis），不写成三个硬编码例子。
断言语义，不断言实现细节。
"""
from hypothesis import given, strategies as st

from services.api.sync import Field, Note, merge_notes


def _note_strategy():
    field = st.builds(Field, value=st.text(max_size=20), ts=st.integers())
    meta = st.dictionaries(st.text(min_size=1, max_size=5, alphabet="abcde"), field, max_size=5)
    return st.builds(Note, id=st.just("n1"), body=st.text(max_size=50), metadata=meta)


@given(a=_note_strategy(), b=_note_strategy())
def test_merge_is_commutative(a, b):
    """与到达顺序无关：merge(a,b) == merge(b,a)。"""
    assert merge_notes(a, b) == merge_notes(b, a)


@given(a=_note_strategy(), b=_note_strategy())
def test_no_body_loss(a, b):
    """正文不丢失：合并后两份正文都在。"""
    m = merge_notes(a, b)
    assert a.body in m.body
    assert b.body in m.body


def test_keeps_both_bodies_and_marks_conflict():
    """正文不同时保留两份并标记冲突（不做截断或三方合并）。"""
    a = Note(id="n1", body="正文A", metadata={})
    b = Note(id="n1", body="正文B", metadata={})
    m = merge_notes(a, b)
    assert "正文A" in m.body
    assert "正文B" in m.body
    assert "CONFLICT" in m.body


def test_metadata_field_level_last_write_wins():
    """元数据按字段级最后写入优先，依据记录自带时间戳，不读系统时钟。"""
    a = Note(id="n1", body="x", metadata={"title": Field(value="旧标题", ts=1)})
    b = Note(id="n1", body="x", metadata={"title": Field(value="新标题", ts=2)})
    assert merge_notes(a, b).metadata["title"].value == "新标题"


def test_metadata_ts_tie_is_deterministic_and_order_independent():
    """时间戳相同也必须与到达顺序无关（确定性 tie-break）。"""
    a = Note(id="n1", body="x", metadata={"k": Field(value="aaa", ts=5)})
    b = Note(id="n1", body="x", metadata={"k": Field(value="zzz", ts=5)})
    assert merge_notes(a, b) == merge_notes(b, a)
