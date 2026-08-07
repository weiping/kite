"""结构化分类契约测试：触发词→任务、日期→日程、兜底笔记、标题、多类。"""
from hypothesis import assume, given, strategies as st

from services.capture.classify import ACTION_WORDS, DATE_WORDS, classify


@given(word=st.sampled_from(sorted(ACTION_WORDS)), rest=st.text(max_size=15))
def test_action_word_produces_task(word, rest):
    """含任务触发词的文本 MUST 产出任务（property）。"""
    r = classify(f"{rest}{word}某事")
    assert len(r.tasks) >= 1


@given(text=st.text(min_size=2, max_size=30))
def test_plain_text_becomes_note(text):
    """不含触发词/日期的文本 MUST 归笔记、不出任务（property）。"""
    assume(not any(w in text for w in ACTION_WORDS))
    assume(not any(w in text for w in DATE_WORDS))
    r = classify(text)
    assert len(r.notes) >= 1
    assert len(r.tasks) == 0


def test_multi_category():
    """一条文本同时含日期句与任务句 → 同时产出日程与任务。"""
    r = classify("明天开会。要买牛奶。")  # 明天开会→event, 要买牛奶→task
    assert len(r.tasks) >= 1
    assert len(r.events) >= 1


def test_title_generated():
    """每条产出 MUST 含非空标题。"""
    r = classify("随便记一句话。")
    assert r.items
    assert all(i.title for i in r.items)
