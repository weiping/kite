---
id: REQ-NOTIFY-ISOLATION
level: MUST
status: accepted
---

# REQ-NOTIFY-ISOLATION 离线通知存储隔离

两服务（Agent 编排层、API Server）的离线通知存储 MUST NOT 互相覆盖。

## Test
- 确定性探索引擎：差分测试——同一序列打两个行为应当等价的服务，比对响应与副作用。
- 典型缺陷：两边默认写同一个库位，单看代码都对，代码评审几乎不可能发现，差分测试立刻抓到结果不一致。
