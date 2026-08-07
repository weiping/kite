# Phase 5: Kite 组件库

## 1. Design Tokens

> 与 `docs/ixd/DESIGN.md` **同源**。此处用 CSS 变量名，值见 DESIGN.md（YAML）。
> 改 token 时两处同步（见 phase6 同步规则）。

### Color
| CSS 变量 | 值（from DESIGN.md） |
| --- | --- |
| `--color-primary` | #3b82f6 |
| `--color-surface` | #ffffff |
| `--color-on-surface` | #1a1a1a |
| `--color-danger` | #ef4444 |
| `--color-primary-dark` | #60a5fa |
| `--color-surface-dark` | #141414 |
| `--color-on-surface-dark` | #e8e8e8 |

### Typography
| CSS 变量 | 值 |
| --- | --- |
| `--font-family-zh` | PingFang SC |
| `--font-family-en` | Inter |
| `--font-size-body` | 14 |
| `--font-size-h1` | 24 |

### Spacing
| CSS 变量 | 值 |
| --- | --- |
| `--space-sm` | 8px |
| `--space-md` | 16px |
| `--space-lg` | 24px |

## 2. 组件规范

### C01 VoiceButton（语音速记按钮）
- 用途：长按录音、松手提交、上滑取消（REQ-CAP-VOICE）
- 尺寸：72×72 FAB，底部居中
- 状态：idle / recording（波纹）/ processing（加载圈）
- token：bg `--color-primary`，icon `--color-surface`

### C02 TextCapture（文字输入）
- 用途：文字速记入口，点击展开
- 状态：collapsed（一行）/ expanded（多行编辑）

### C03 TimelineItem（时间线条目）
- 用途：时间线里的笔记/任务/日程
- 状态：default / conflict（REQ-SYNC-CONFLICT 冲突标记）/ pending-sync（离线待传）

### C04 SearchBar（自然语言检索）
- 用途：一句话提问入口（REQ-RET-NLSEARCH）
- 状态：idle / searching / offline-degraded

### C05 NoteCard（笔记卡片）
- 用途：笔记展示，含来源标注（REQ-CAP-VOICE-RAW）
- 状态：default / expanded（看原文副本）

### C06 TaskItem（任务条目）
- 用途：待办，含完成态
- 状态：todo / done
