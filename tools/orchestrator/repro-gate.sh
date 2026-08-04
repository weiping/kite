#!/usr/bin/env bash
# tools/orchestrator/repro-gate.sh <contract> <fix_commit>
# 红绿红三段：修复前必须红、修复后必须绿、还原修复必须再红。
# 第三段是关键：它证明"这个测试确实在检验这个修复"，区别于普通 CI。
# 参考实现：用独立工作树而不是暂存区，避免污染当前工作区。
set -euo pipefail

CONTRACT=$1; FIX=$2
IMPL_PATHS=$(python -m spec_runner allowed-changes "$CONTRACT" --only-impl)
WT=$(mktemp -d)
git worktree add -q "$WT" "$FIX"
trap 'git worktree remove -f "$WT"' EXIT
cd "$WT"

run() { python -m spec_runner run "$CONTRACT" --root . --quiet; }

# 第一段：还原实现，测试必须红
git checkout "$FIX~1" -- $IMPL_PATHS
if run; then echo "REPRO-GATE 失败：修复前测试就是绿的，它没在检验这个修复"; exit 1; fi

# 第二段：恢复实现，测试必须绿
git checkout "$FIX" -- $IMPL_PATHS
if ! run; then echo "REPRO-GATE 失败：修复后仍然红"; exit 1; fi

# 第三段：再次还原，必须再红（确认第一段不是偶然）
git checkout "$FIX~1" -- $IMPL_PATHS
if run; then echo "REPRO-GATE 失败：还原修复后测试仍然绿"; exit 1; fi

git checkout "$FIX" -- $IMPL_PATHS
echo "REPRO-GATE 通过"
