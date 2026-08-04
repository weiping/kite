"""协议抗毒化：乱序/非法/边界报文不挂死、不波及其他会话。

Level: property —— 用 hypothesis 遍历报文空间，不是几个硬编码例子。
"""
from hypothesis import given, strategies as st

from services.api.proto import InvalidPacket, Session, process_packet


def _packet_strategy():
    valid = st.fixed_dictionaries({"type": st.text(min_size=1, max_size=5),
                                   "data": st.text(max_size=10)})
    invalid_dict = st.dictionaries(st.text(min_size=1, max_size=3), st.text(max_size=5),
                                   max_size=3).filter(lambda d: "type" not in d)
    non_dict = st.text()
    return st.one_of(valid, invalid_dict, non_dict)


@given(stream=st.lists(_packet_strategy(), max_size=25))
def test_poison_does_not_hang_or_leak(stream):
    """打到 S1 的任意报文流（含乱序/非法/非 dict）不挂死、不影响 S2。"""
    s1 = Session("s1")
    s2 = Session("s2")
    s2.state["keep"] = "v"
    for pkt in stream:
        try:
            process_packet(s1, pkt)
        except (InvalidPacket, TypeError):
            pass
    # 走到这里即证明 S1 未挂死；S2 状态必须原样不变
    assert s2.state == {"keep": "v"}
