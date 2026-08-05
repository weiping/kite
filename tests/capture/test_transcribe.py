"""转写清洗契约测试：保留原文副本（property）+ 元信息可追溯（unit）。"""
from hypothesis import given, strategies as st

from services.capture.transcribe import clean_transcript


@given(raw=st.text(max_size=100), model=st.text(min_size=1, max_size=10),
       prompt=st.text(min_size=1, max_size=10))
def test_clean_keeps_raw(raw, model, prompt):
    """清洗后必须保留原始转写副本（INV-006）。"""
    result = clean_transcript(raw, {"model_version": model, "prompt_version": prompt})
    assert result.raw == raw
    assert result.clean is not None


def test_meta_traceable():
    """AI 生成内容可追溯到模型与提示词版本（charter 第4条）。"""
    result = clean_transcript("嗯那个测试", {"model_version": "whisper-small", "prompt_version": "v1"})
    assert result.meta["model_version"] == "whisper-small"
    assert result.meta["prompt_version"] == "v1"
