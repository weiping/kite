# 复盘：Kite L1 地基 + M0 语音速记（2026-08-04 ~ 08-07）

> 一个会话从空目录建起完整的 L1 自主开发地基 + M0 第一个需求走完全程 + CI 全绿 + UI 设计 + 博客。18 commit，77 测试。

## 成果全景

| 层 | 产出 | 状态 |
| --- | --- | --- |
| **方案存档** | `docs/index.md`（L1→L3 全文）+ GitHub Pages 博客 | ✅ 上线 |
| **PRD** | `prd.md`（7 模块功能定义，竞品调研） | ✅ |
| **规约层** | agent-spec 1.2.0 Intent Compiler（lint/graph/plan/traceability/import 全链） | ✅ |
| **执行器** | `tools/spec-runner`（五态 + boundary + bridge，77 测试） | ✅ |
| **桥接** | `tools/ixd2spec`（页面→golden）、`tools/dtcg2flutter`（DTCG→Flutter） | ✅ |
| **UI 设计** | ixd-design P1-P6（`docs/ixd/`）+ DESIGN.md（14 令牌） | ✅ |
| **CI** | `verify.yml` 全门禁（GitHub Actions 全绿） | ✅ |
| **M0 语音速记** | 需求→决策→契约→后端(转写/排队)+客户端(状态机/录音) | ✅ 录音就绪，whisper 待 |
| **样板** | 离线笔记冲突合并（属性测试，bridge skip→pass） | ✅ |

## 关键架构决策（下次别推翻）

1. **规约用 agent-spec 不自研**：`knowledge/requirements/*.md`（kind: requirement）→ `specs/*.spec.md`（四要素）→ `requirements plan`（0 diagnostic）
2. **执行器外接**：agent-spec verify 对 py/dart 判 skip → `spec-runner bridge` 跑真实测试 → `resolve-ai` 注入（skip→pass）。这是方案「执行器绑定 Rust，Python/Dart 外接」的工程闭环
3. **五态而非两态**：pass/fail/skip/uncertain/pendingreview；skip 永远阻断；uncertain 工具缺失≠被证伪
4. **ixd-design 保留 CSS 变量 + 额外产出 DESIGN.md**（Google 格式）：同源双写，DESIGN.md 享 `@google/design.md` CI 门禁
5. **whisper 端侧（A）**：满足 charter 不出站 + 离线优先；模型下发 D2，二进制 D1

## 踩坑大全（下次别重蹈）

### agent-spec
- spec frontmatter **无开头 `---`**（直接 `spec:` 开头）
- requirement 必须 `kind: requirement` + 标准段（Problem/Requirements/Scenarios/Dependencies/Source Trace/Open Questions）
- decision 标准段名：Context/Decision/Consequences/Alternatives Considered（中文段名报错）
- Open Questions 要纯 `None.`（加说明仍判 blocked）
- requirements import 的 marked blocks：`<!-- agent-spec:requirement id=... -->...<!-- /... -->`

### CI 真跑校准（本地绿≠CI绿）
- `spec-runner[test]` extras 才含 pytest（默认只 pyyaml）
- flutter test 在 CI non-TTY 用 **emoji reporter**（🎉 N test），本地 TTY 才有 `+N:` → `_parse_visible` 要兼容两种
- exit 1 + "No module named pytest" 应判 **uncertain**（工具缺失）非 fail
- flutter test 用 `--plain-name` 筛选，不认 pytest 的 `::test`
- cargo 国内慢 → rsproxy 镜像 + `CARGO_NET_TIMEOUT/RETRY`

### Flutter
- `flutter create` 在非标准项目崩（TypeError）→ 干净目录生成再拷 `macos/`
- 自定义类名别和插件库类名撞（`AudioRecorder` vs record 库的）→ `import as rec`
- macOS 麦克风需 entitlements `audio-input` + sandbox 下临时目录可写

### ixd-design 集成
- P4 状态段标题 `## Section 5: 状态机` vs ixd2spec 找 `## 状态` → ixd2spec 正则放宽（## 行含"状态"）
- skill 产出 `doc/ixd` vs kite 用 `docs/ixd` → 统一 docs/ixd

### 网络/Git
- GitHub credential 链有 `GC-CBot` 旧 token 污染 → 用 `x-access-token:$(gh auth token)` 直推
- workspace 是大仓库，kite 要独立 → `git rm --cached -r dev/kite` + workspace `.gitignore`

## 下一步（优先级）

1. **whisper 端侧转写**（M0 最后拼图）：sherpa_onnx 插件 + 模型下载脚本（200MB 不入库）+ 转写代码接 voice_entry
2. **更多 M0 需求**：结构化分类（REQ-STRUCT-CLASSIFY）、自然语言检索（REQ-RET-NLSEARCH）
3. **L1.5**：风险分级抽检（policy/risk.rego 已有）、审计包（tools/audit-seal）、影子运行
4. **nightly V5**：变异测试接线，进入 L1 出口准则

## 恢复上下文的快捷命令

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/ tools/ixd2spec/tests/ tools/dtcg2flutter/tests/ tests/ -q  # 77 测试
agent-spec requirements plan          # 0 diagnostic
agent-spec lint-knowledge --gate      # 0 error
.venv/bin/python -m spec_runner bridge specs/task-cap-voice.spec.md  # 4 场景全 pass
flutter analyze                       # apps/mobile 0 error
gh run list --workflow verify.yml     # CI 全绿
```
