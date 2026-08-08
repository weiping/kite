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

## 续作11：L2-1 回归有效性验证（反自洽链层3，08-08）

L2 第一根柱子的一层——反自洽验证链层 3（index.md 点名「整条链最省钱」）。

**成果**
- `spec-runner regression-check <spec>` 子命令：假设工作区含修复，`stash` 还原跑测试（期望红）→ `pop` 恢复跑（期望绿）
- `_regression_report`：`before(还原)=FAIL + after(修复)=PASS` 才有效；`before=PASS` = 测试没测 bug（自洽但不正确）→ invalid 退 1
- 三段规则（前红/后绿/还原红）由 before FAIL + after PASS 覆盖（还原红 = before）
- 零模型调用，两次机械执行；TDD 4 task，80 测试绿

**范围说明**：regression-check 假设工作区含修复（未 commit），主要给 Agent 修复任务会话内验证（修完跑一遍再 commit）。CI 接线需 commit-ref 模式（HEAD vs HEAD~1），留后续。

**L2 现状**：柱二·层 3 已建。待建：柱二其余层（Test Author 隔离/变异/Verifier/独立裁决）+ 柱三探索引擎 + provenance + 影子运行达标。L2 切换（去人审）需 12 周数据 + 四柱齐全，kite 还早。

## 续作12：L2-2 变异测试 + provenance（08-08）

L2-2 两件：

**变异测试（柱二层4）**：`pyproject [tool.mutmut]`（source_paths = services/ + spec_runner/）+ nightly.yml 接线（mutmut run/results，不阻断，workflow_dispatch 手动触发）。本地验证 32 files mutated（配置对，跑测试慢留 nightly CI）。变异得分是 L2 达标观测（关键模块 ≥80%），nightly 走趋势不阻断。

**provenance（需求接受机制）**：`spec-runner provenance-lint` 子命令，检查 requirement Source Trace + stated，收集低/中置信 inferred 升人审。**真验证发现 kite 4 个 requirement 缺 stated**（REQ-INV-003/NOTIFY-ISOLATION/PROTO-POISON/SYNC-CONFLICT，格式是 `- prd:`/`- invariant:` 没加 `stated:` 前缀），已补——provenance-lint 抓到了真实漏洞。修复后 valid=true。

**L2 现状**：柱二·层 3（回归有效性）+ 层 4（变异）+ provenance 已建。待建：柱二其余（Test Author 隔离 / Verifier 五项 / 独立裁决）+ 柱三探索引擎（差分/模糊/混沌）+ 影子运行达标。

## 续作13：L2-3 柱三确定性探索（08-08）

kite **属性测试已遍布**（proto/classify/search/transcribe/queue/isolation/sync 全有 hypothesis `@given`，proto 防毒已是流遍历探索）= 柱三基础已有，不是从零。

L2-3 增强：nightly 加 hypothesis 长探索步骤（`HYPOTHESIS_MAX_EXAMPLES=1000`，CI 默认 100），过夜探索抓白天漏的，`--hypothesis-show-statistics` 出统计。变异（柱二层4）+ 探索（柱三）都在 nightly。

状态机（`RuleBasedStateMachine`）/ 差分 / 混沌：kite proto 简单（`@given` lists 已是流探索）+ 单实现 + 服务少，ROI 低，后续按场景。

**L2 现状**：柱二（层3 回归 + 层4 变异）+ provenance + 柱三（属性探索已遍布 + nightly 长探索）已建。待建：柱二其余（Test Author 隔离 / Verifier 五项 / 独立裁决）+ 柱三状态机/差分/混沌 + 影子运行达标（L1.5→L2 切换准入）。

## 续作14：L2 影子观测 + Test Author 隔离（08-08）

**影子运行观测（L1.5→L2 切换准入）**：`spec-runner shadow-report` 读 `.out/shadow.jsonl`，算 level 分布 + deny 率 + 一致性（R0→auto / R1-R3→review 算 match，`human_decision` null 不比）。真验证本地 25 条（全 R0，deny_rate 0.48，consistency 待 `human_decision` 回填）。一致性 ≥90% 是切换准入。

**Test Author 隔离（柱二层2）**：kite 测试从 spec 派生（`contract.py` 解析 Test selector），约定编写只看 spec G/W/T 不参考实现（防「测试照实现写」）。属流程约束，solo 靠约定（index L2 落地现状 + README 记）。

**概率性基建（柱二层5/6）延后**：Verifier 五项 / 独立裁决需真模型调用 + 成本，kite 无模型基建（bridge 用 spec-runner mock，非真 AI），延后到引入真 AI verifier。

**L2 确定性验证体系完成**：柱二确定性层（层3 回归 + 层4 变异）+ 柱三探索 + provenance + 影子观测。剩概率性（模型基建）+ 影子 12 周达标。

## 续作15：L2 verify-ai（层5 Verifier + 层6 独立裁决，概率性，08-08）

L2 柱二最后两层（概率性，接智谱 GLM）：

**verify-ai 子命令**：调智谱（`ZHIPUAI_API_KEY` 环境变量 + CI secret + `.gitignore .env` 三保险），对 spec scenario 跑：
- 层5 Verifier：scenario + targets 代码 → 检查附带损害/越界（`VERIFY_OK/FAIL`）
- 层6 独立裁决：不假设契约对，独立推演 vs 契约，找洞（`ADJUDICATE_OK/CONCERN`）

**CI**：nightly 条件触发（有 KEY 跑，不阻断，concerns 报告）。成本控制（nightly 不每次）。TDD mock 智谱 client，6 测试绿。

**L2 反自洽链全六层完成**：层1（测试从规约派生，kite 已有）+ 层2（Test Author 隔离约定）+ 层3（回归有效性）+ 层4（变异）+ 层5（Verifier）+ 层6（独立裁决）。

**L2 确定性 + 概率性验证体系全建**。剩影子 12 周达标（L1.5→L2 切换准入，`human_decision` 回填 + 观察窗口）。

## 续作16：L3 机制（charter-lint + monthly-audit，搭机制待用，08-08）

L3 是搭机制不实跑（需 L2 达标才切换）。index.md 明确「机制要在 L1 阶段建好，不能等 L2 跑顺再补」。

**charter-lint**：扫 requirements 检查 Source Trace 引用 charter（L3 一致性论证来源）。真验证 11 requirements，7 引用 charter（63.6%），4 缺（INV-003/NOTIFY-ISOLATION/PROTO-POISON/SYNC-CONFLICT）——工具抓到真实缺口。

**monthly-audit**：月度累积效应审计骨架（shadow 趋势 + 变更计数，escape_defects 待 L2 达标后追踪）。monthly.yml 月度 cron（每月 1 号）。

**L3 机制搭好待用**：charter 一致性 + 月度审计。需求候选管线（净化/论证/预算）大件，L3 切换时再建。L3 切换需 L2 达标（影子 12 周 ≥90%）。

**L1-L3 全级机制搭完**：L1（地基）+ L1.5（关卡概率化，全闭环）+ L2（反自洽链全六层 + 柱三 + provenance + 影子 + verify-ai）+ L3（charter-lint + monthly-audit）。

## 续作17：L2 加速方案（拒绝跳级后，08-08）

用户要求「取消影子 12 周达标，直接切 L3」——**我拒绝了**（index.md + Berkeley 核心警告的「组织跳级」），提加速方案，用户选。

**为什么拒绝直接切**：影子达标不是官僚门槛，是把「去人审安全吗」变可测量的；`human_decision` 全 null = 没数据盲切；R3 自动合 = Agent 改自己门禁 = 没门禁；index.md 整篇就在反对跳级。

**加速方案（不跳级）**：
- **human_decision 回填**：auto-merge job 决定后 comment「📊 human_decision: auto/review | level: RX」（PR 留记录，shadow-report 后续可读算一致性）——让 4 周后有数据判一致性
- **窗口 4 周**：solo 加速（设计保持 12 周通用，落地缩 4 周）
- **L3 试点**：label 观察后续（不盲自动合）

**教训**：用户提危险变更（跳级）时，agent 要 propose 风险 + 替代 + wait，不盲从。这是 AGENTS.md「安全变更问」的实战。

## 待做：L1/L1.5 工作流复用 Skill（08-08 讨论，暂缓）

把 L1/L1.5 工作流抽象成 pi skill 复用到其他项目。方案要点（避免重想）：

- **分层**：配置类（risk.rego R3 路径/白名单、verify.yml、spec 骨架、AI-BOM 组件）纯提示词生成；复杂工具（spec-runner）用「行为 spec + Python reference」；risk.rego/opa/agent-spec 直接复用（语言无关）
- **skill 结构**：`SKILL.md`（建立步骤+决策点）+ `spec-runner.spec.md`（行为规约：CLI 接口/五态/退出码/risk.rego input 格式）+ `reference/`（Python 参考实现）+ `templates/`（配置模板）+ `REFERENCE.md`（理念精要）
- **关键判断**：spec-runner 纯提示词生成风险高（五态/退出码/input 格式是跨项目契约，易漂移）→ 用规约 + 参考实现最稳；这也是「用规约建工具」的自指验证
- 触发词：「建立 L1 地基」「复用 kite 工作流」「AI 自主开发地基」
- 等 kite 跑顺 + 验证一两个项目后，再投入 spec-runner 通用化/发布

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
