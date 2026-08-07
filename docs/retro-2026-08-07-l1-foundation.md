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

## 续作：whisper 端侧转写（08-07）

M0 最后拼图。成果 + 新踩坑：

**成果**
- `whisper_transcriber`（sherpa_onnx 1.13.4）：OfflineRecognizer + readWave + stream + acceptWaveform
- `audio_recorder` 录 wav（16k mono PCM16，sherpa 要求）
- main 接转写：模型就绪则转写、未装降级仅录音
- 模型下载脚本（sherpa-onnx-whisper-small）
- **flutter build macos 成功**（native 链接验证：sherpa + onnxruntime + record 全通过）

**新踩坑**
- macOS 部署目标：flutter create 默认 10.15，Xcode 27 要 12.0+，且 `record_macos` 的 `auAudioUnit` 要 13.0+ → Podfile platform 13.0 + post_install 强制 Pod target 13.0 + pbxproj 13.0
- sherpa API：`OfflineRecognizerConfig(model:)` 不是 `modelConfig:`；`OfflineRecognizer(config)` 位置参数；`decode(OfflineStream)` 需先 `readWave` + `acceptWaveform`
- record 7.x 类名 `AudioRecorder` 与自定义类撞 → `import as rec`
- 模型实际 **609MB**（非预估 200MB），github releases 国内 ~350KB/s，约 30 分钟 → 用 hf.qhduan.com / modelscope 镜像

**仍待（真跑）**
- 模型下载（609MB，慢）→ 放 app Documents（`~/Library/Containers/com.kite.kiteMobile/Data/Documents/whisper-small/`）→ `flutter run -d macos` 长按录音看转写
- record wav 在 macOS 真产出标准 wav（需 run 验证 readWave 能读）

## 续作2：M0 数据流闭环 + 端到端（08-07）

M0 后端纯逻辑链完整 + 客户端 Dart 端侧全链 + 串联。

**成果**
- 后端闭环：classify→store→search（Python，属性测试，demo 验证 `classify(文本)→持久化→search 带来源`）
- 客户端 Dart 全链：`lib/capture/{classify,search}` + `lib/store/store`（复刻规则）+ main.dart 串（录音/文本→classify→store→时间线+搜索）
- 两端契约驱动：同一 spec 规范 Python+Dart，各自属性测试/flutter_test（防漂移）
- whisper 未装时文本输入 fallback（端到端框架不依赖模型可跑）

**新踩坑**
- **sherpa_onnx API**：`OfflineRecognizerConfig(model:)` 非 modelConfig:；`OfflineRecognizer(config)` 位置参数；`decode(OfflineStream)` 需先 `readWave` + `acceptWaveform`（非直接传 path）
- **hypothesis @given 与 pytest tmp_path fixture 冲突** → 用 `tempfile.TemporaryDirectory`
- **Dart import 相对路径**：子目录文件（store/search）import 同目录用 `'classify.dart'` 或 `package:`，不能 `'capture/classify.dart'`（相对自身目录解析错）
- **`expect(bool, isTrue)` 在此环境报参数数错** → 用 `true` 替代（同效）
- 模型实际 609MB（非 200MB），github 国内 ~350KB/s，会话内下不完 → 需代理/mirror

**M0 状态**：端到端框架两端完整，**whisper 模型下载是唯一阻塞**（网络）。文本路径现在能 `flutter run -d macos` 跑通全链。

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
