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

## 续作3：whisper 模型下载解锁（08-08）

模型下载阻塞已解除（609MiB 下完，校验通过）。

**镜像方案（国内）**：github release-assets（release-assets.githubusercontent.com）国内基本不通。`MIRROR` 环境变量选镜像，按速度排序：
- `ghfast`（默认）：~300-380KB/s，~32 分钟下完 ✅
- `ghproxy`（gh-proxy.com）：~155KB/s
- `llkk`（gh.llkk.cc）：~186KB/s
- hf-mirror.com 的 k2-fsa 仓库 401（私有/需授权），hf 路线不通
- retro 旧版写的 `hf.qhduan.com` 已连不上（HTTP 000），作废

**脚本改进**（`apps/mobile/scripts/download-whisper-model.sh`）：
- 加 `MIRROR` 选择 + 断点续传（tarball 留 `.cache/`，`--clean` 清）
- **大小校验**（EXPECTED=639387718，不对报错）
- 删非 int8 量化版（`small-decoder.onnx` + `small-encoder.onnx` ≈ 970MiB，端侧用不到）→ 1.3G 降到 359M
- **rename 去 `small-` 前缀** → 代码引用 `encoder.int8.onnx`/`decoder.int8.onnx`/`tokens.txt`（模型无关）

**新踩坑**
- **解压文件名带 `small-` 前缀**：sherpa 官方包是 `small-encoder.int8.onnx`/`small-decoder.int8.onnx`/`small-tokens.txt`，但代码写的是无前缀名。修复点在下载脚本（rename），非代码——让代码保持模型无关，换 base/medium 时只改脚本
- **模型实际 609MiB**（639,387,718 字节），非脚本旧注释的 200MB（已改注释）
- **sherpa_onnx 1.13.4 必须先 `initBindings()`**：创建 OfflineRecognizer 前没调用 `sherpa.initBindings()` 会抛 `Exception: Please initialize sherpa-onnx first`（包注释 `sherpa_onnx.dart:12` 明说 "call initBindings once before any runtime object"）。续作1 记了 API 调用细节但漏了这步。症状隐蔽：app 不崩（async 异常被 framework 吞），但 `_recognizer` 未赋值 → `isReady=false` → FAB 显示条件 `recording || isReady` 为假 → 录音按钮为 null，UI 只剩文本输入框。修复：`WhisperTranscriber.init()` 第一行加 `sherpa.initBindings()`，重新 run 日志 0 异常

**已就位（08-08）**
- 容器 `~/Library/Containers/com.kite.kiteMobile/Data/Documents/whisper-small/` 已拷入 3 文件（encoder/decoder.int8.onnx + tokens.txt，359M）
- 修复 `initBindings()` 后 `flutter run -d macos` 日志 0 异常，`isReady=true`，FAB 录音按钮正常显示（注：此前“open .app 启动未崩”是误判——open 无终端看不到 init 抛的 `Please initialize sherpa-onnx first`，app 不崩只是 async 异常被吞。教训：验证 native/FFI init 必须看终端日志，不能凭“进程没退”）
- bz2 已 trash（解压后冗余，留了空 .cache/ 目录）

**仍待（用户录音验证，agent 无法代劳真声输入）**
- `flutter run -d macos` 长按录音 → 看 sherpa `decode` 出转写文本
- record wav 在 macOS 真产出标准 wav（需 run 验证 `readWave` 能读）

## 续作4：UI 真机验证 + 4 个串儿 bug（08-08）

下完模型 `flutter run` 真机验证，揪出 4 个**独立** bug（任一个都让语音输入用不了），逐个修：

1. **sherpa.initBindings() 漏调**（已记续作3新踩坑）→ `_recognizer` 未赋值 → `isReady=false` → FAB 不显示。app 不崩（async 异常被吞），隐蔽
2. **MaterialIcons 字体没打包**：`pubspec.yaml` 缺 `flutter: uses-material-design: true` → `FontManifest=[]`、flutter_assets 无字体 → 所有 `Icons.xxx`（mic/search/send）显示问号。修复：pubspec 加该段
3. **macOS Info.plist 缺 NSMicrophoneUsageDescription**：entitlements 有 `device.audio-input` 但 Info.plist 无 usage description → record 库 `AVCaptureDevice.default(for:.audio)` 拿不到设备。修复：Info.plist 加 `NSMicrophoneUsageDescription`
4. **录音按钮手势竞争**：`GestureDetector` 包 `FloatingActionButton`，FAB 内层 tap recognizer 抢手势，外层 `onLongPressStart` 不触发 → 长按无反应。修复：改 `Listener(onPointerDown/Up)` + `Container`（`BoxShape.circle`），按住录音/松手转写

**教训**：验证 native/FFI/平台能力必须看终端日志，不能凭“进程没退”或“按钮在不在”。这次靠 `debugPrint` 逐层实证（docsDir/exists/isReady/hasPermission/wav）才定位到每层

**录音验证搁置（环境限制，非代码）**
- 修完 1-4 后，record 库仍报 `Input device not found from available list`（`AVCaptureDevice.default(for:.audio)` 返回 nil）
- `system_profiler SPAudioDataType` 查无可用音频输入设备 → 当前环境（无麦克风）无法验证录音→转写闭环
- 已验证通过的链路：模型下载/校验/解压、`initBindings`、`isReady=true`、Listener 手势触发（record start/submit 日志反复出现）、字体/图标渲染、按钮圆形
- 待有音频设备的环境再跑：长按 → wav → `transcribe` → 时间线

## 续作5：L1.5 风险分级接线（阶段1，08-08）

L1.5 三件中的第一件——风险分级接线——完成并上 main。

**成果**
- `spec-runner risk` 子命令：`collect_risk_input()`（复用 affected）→ `evaluate_risk()`（subprocess `opa eval policy/risk.rego`）→ `{level: R0-R3, deny: [...]}`
- opa 缺失明确报错（`FileNotFoundError`，exit 2）；`deny` 非空 exit 1（gate）
- CI `verify.yml` 加 `open-policy-agent/setup-opa@v2` + risk gate 步骤（输出 level，deny 阻断）
- TDD 5 task，全量 97 测试绿（+20 risk）；CI 真实输出 `level: R1`（本次改动超 50 行），deny 空，gate 过
- 实施计划存档 `docs/superpowers/plans/2026-08-08-l1.5-risk-wiring.md`

**踩坑**
- opa 本地 `brew install opa`（1.19.0），CI `setup-opa@v2`；rego v1 query `data.kite.risk` 取 package 所有 public，提取 `level`/`deny`
- TDD 分段：`evaluate_risk` 拆 Task2（opa 缺失检测）+ Task3（opa eval 逻辑），每段测试先行（避免代码先于测试）
- setup-opa@v2 走 Node 20（deprecated warning，未来换 action 版本）

**阶段2 待办（L1.5 继续）**
- R0 自动合并：GitHub branch protection + auto-merge（risk gate 输出 level 驱动）
- `dangling_selectors`/`boundary_violations` 实填（扫所有 specs allowed_changes 并集 vs changed）
- 影子运行：记录 level vs 人审决定，算一致性（L1→L1.5 切换准入，≥90%）
- audit-seal 审计包（空目录待实现，出口准则完备率 100%）

## 续作6：L1.5 阶段2（boundary 实填 + 影子记录 + R0 自动合并，08-08）

L1.5 阶段 2 完成，**R0 自动合并真验证通过**（PR #3 docs 小改 → contract pass → 自动 MERGED）。

**成果**
- boundary_violations 实填：collect_risk_input 扫所有 specs allowed_changes 并集 + 白名单 vs changed
- 影子记录：risk 命令追加 `.out/shadow.jsonl`（ts/commit/level/deny/changed_files/human_decision）
- repo auto-merge + delete_branch_on_merge 开启；main branch protection（require PR + check `contract` + enforce_admins=false 保留 owner 紧急绕过）
- verify.yml：contract job 输出 risk level + auto-merge job（R0 → `gh pr merge --auto --squash` / 非 R0 → comment）
- **R0 自动合并闭环验证**：PR #3（docs 小改）→ R0 → contract pass → 自动合并

**踩坑（5 个，CI 真跑才暴露）**
1. **CI `git diff HEAD` 看 pubspec.lock 副作用**：flutter pub get 重生成 lock，git diff HEAD 捕获工作区副作用而非 PR committed 改动。治本：collect_risk_input 改用 `origin/main...HEAD`
2. **needs-review label 不存在**：`gh pr edit --add-label` 对不存在 label 报错 → 改 `gh pr comment`（权限够 + 免预建）
3. **R3 触发**：改 `.github/workflows/` → R3（最严档），设计如此（CI 配置敏感）
4. **branch protection contexts**：实际 check 名是 `contract`（job name），不是 `verify / contract`。required_status_checks.contexts 要匹配 check run name
5. **auto-merge job 没 checkout**：`gh pr merge` 在非 git 目录失败 → 加 `--repo weiping/kite` 免 checkout

**教训**：CI workflow 的 git/gh 行为必须真跑验证（本地测不出 diff 副作用、check 名、checkout 缺失）。每个假设都要 CI 实证。

**L1.5 现状**：阶段 1（risk 评估）+ 阶段 2（boundary 实填 + 影子 + R0 自动合并）完成。关卡概率化闭环：R0 自动合 / R1-R3 人审。dangling_selectors 待接。

## 续作7：L1.5 audit-seal 审计包（阶段1，08-08）

L1.5 第二件——审计包收集能力建立。

**成果**
- spec-runner `audit-seal` 子命令：`collect_ai_bom`（CycloneDX 1.5 BOM）+ `collect_audit_package`（制品引用 + 元数据）→ 写 `.out/audit/<commit>.json`
- 原则：只收集不生产，AI-BOM 用 CycloneDX（不自造格式）；制品只存引用不复制内容（轨迹外置）
- AI 组件：sherpa-onnx-whisper-small（模型）/ agent-spec / spec-runner / opa（工具）
- 制品引用：evidence / risk / shadow / design_lint / evals / mutation
- verify.yml 加 audit-seal step，CI 验证生成 `.out/audit/7e57c9e328.json`
- TDD 4 task，69 测试绿

**阶段后续**
- 保留期限（R2+永久 / R1两年 / R0六月）+ 入库归档
- AI-BOM 动态提组件版本（从 pubspec/Cargo，当前硬编码）
- dangling_selectors 接入（risk.rego input 补全）

**L1.5 现状**：阶段1（risk 评估）+ 阶段2（boundary / R0 自动合并）+ audit-seal（收集能力）。出口准则：R0 自动合并 ✓ + 审计包收集 ✓（完备率 / 保留期限 / dangling 待续）。

## 续作8：dangling_selectors 接入（08-08）

risk.rego input 补全——`collect_risk_input` 填 dangling_selectors。

- `_collect_dangling_selectors`：扫所有 specs 的 scenario test selector，文件部分不存在 → dangling（最小，用 contract.py 解析；函数级 dangling 留 agent-spec 后续）
- kite 当前 specs 一致 → dangling 0（能力建立，未来 spec 引用不存在测试 → deny）
- risk 命令本地验证：level R0, deny 空

**L1.5 风险分级 input 完整**：changed_files/lines + boundary_violations + dangling_selectors 三者全填，risk.rego 的 deny 两条规则都能触发。

## 续作9：audit-seal 阶段2（保留期限 + 入库，08-08）

audit-seal 收尾：保留期限 + 入库归档。

- `_retention(risk_level)`：R2+永久 / R1两年 / R0六月（index.md L1.5 准则），collect_audit_package 加 retention 字段
- `audit-seal --archive`：入库 `audit-seal/<commit>.json`（永久保留）；默认 `.out/audit/`（CI artifact）
- TDD 2 task，74 测试绿

**L1.5 audit-seal 完整**（收集 + retention + 入库）。剩余 AI-BOM 动态版本 / dangling 函数级 = 可选后续（低 ROI，硬编码版本 + 文件级 dangling 已够用）。

## 续作10：L1.5 polish（AI-BOM 动态 + dangling 函数级，08-08）

收尾两件：
- **AI-BOM 动态版本**：`collect_ai_bom` 加 `sherpa_onnx` 组件，version 从 `apps/mobile/pubspec.yaml` 动态提（`_read_pubspec_version`，去 `^` 前缀）
- **dangling 函数级**：`_collect_dangling_selectors` 增强，py 查 `def <func>(`（文件在但函数不在也算 dangling）
- TDD 2 task，76 测试绿

## L1.5 全部完成

risk 评估（R0-R3 + boundary + dangling 函数级 → deny）· R0 自动合并（branch protection）· 审计包（CycloneDX AI-BOM 动态 + 制品引用 + retention + --archive 入库）· 影子记录。关卡概率化闭环全建立。

## 恢复上下文的快捷命令

```bash
cd ~/workspace/dev/kite
.venv/bin/python -m pytest tools/spec-runner/tests/ tools/ixd2spec/tests/ tools/dtcg2flutter/tests/ tests/ -q  # 97 测试
agent-spec requirements plan          # 0 diagnostic
agent-spec lint-knowledge --gate      # 0 error
.venv/bin/python -m spec_runner bridge specs/task-cap-voice.spec.md  # 4 场景全 pass
flutter analyze                       # apps/mobile 0 error
gh run list --workflow verify.yml     # CI 全绿
.venv/bin/python -m spec_runner risk                    # L1.5 风险分级 → {level, deny}
.venv/bin/python -m spec_runner audit-seal              # L1.5 审计包 → .out/audit/<commit>.json（--archive 入库）
```

<!-- R0 自动合并验证2 12:06 -->
