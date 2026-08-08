#!/usr/bin/env bash
# 下载 whisper-small（sherpa-onnx 格式）端侧转写模型。
# 模型 639,387,718 字节 ≈ 610 MiB，不入库（.gitignore 排除 apps/mobile/assets/models/）。
# DEC-CAP-TRANSCRIPTION 选 A 端侧 whisper-small。
#
# 用法：
#   ./apps/mobile/scripts/download-whisper-model.sh [目标目录]
#   MIRROR=ghfast  ./...   选镜像（ghfast|ghproxy|llkk|direct|<自定义前缀>）
#
# 国内默认走 ghfast.top 镜像（实测 ~300KB/s，~35 分钟）。
# 直连 github release-assets 国内基本不通。
# 断点续传：tarball 留在 <DEST>.cache/，重跑脚本自动续传；下完用 --clean 清缓存。
# 校验：下载字节数必须 == EXPECTED_BYTES，否则报错退出。
set -euo pipefail

DEST="${1:-apps/mobile/assets/models/whisper-small}"
EXPECTED_BYTES=639387718
GH_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2"

case "${MIRROR:-ghfast}" in
  ghfast)  MODEL_URL="https://ghfast.top/${GH_URL}" ;;
  ghproxy) MODEL_URL="https://gh-proxy.com/${GH_URL}" ;;
  llkk)    MODEL_URL="https://gh.llkk.cc/${GH_URL}" ;;
  direct)  MODEL_URL="$GH_URL" ;;
  *)       MODEL_URL="${MIRROR}${GH_URL}" ;;  # 自定义前缀，如 https://x.com/
esac

CACHE_DIR="${DEST}.cache"
TARBALL="$CACHE_DIR/model.tar.bz2"
mkdir -p "$CACHE_DIR" "$DEST"

# --clean：仅清缓存
if [ "${1:-}" = "--clean" ]; then
  rm -rf "$CACHE_DIR"; echo "已清缓存 $CACHE_DIR"; exit 0
fi

echo "镜像: ${MIRROR:-ghfast}"
echo "下载 → $TARBALL （断点续传，已存在则续传）"
curl -L --retry 8 --retry-delay 3 -C - -o "$TARBALL" "$MODEL_URL"

ACTUAL=$(stat -f%z "$TARBALL" 2>/dev/null || stat -c%s "$TARBALL")
if [ "$ACTUAL" != "$EXPECTED_BYTES" ]; then
  echo "❌ 大小校验失败：$ACTUAL != $EXPECTED_BYTES（可能镜像截断，换 MIRROR 重跑）" >&2
  exit 1
fi
echo "✅ 大小校验通过 ($ACTUAL 字节)"

echo "解压..."
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
tar -xjf "$TARBALL" -C "$TMP"
SRC=$(find "$TMP" -maxdepth 1 -type d -name "sherpa-onnx-whisper-small*" | head -1)
cp "$SRC"/* "$DEST"/

# 端侧只用 int8 量化版：删非量化的 .onnx（decoder.onnx + encoder.onnx ≈ 970MiB）
rm -f "$DEST"/small-decoder.onnx "$DEST"/small-encoder.onnx
# 去 small- 前缀 → 代码引用 encoder.int8.onnx/decoder.int8.onnx/tokens.txt（模型无关）
for f in "$DEST"/small-*; do
  [ -e "$f" ] || continue
  mv "$f" "$DEST/$(basename "$f" | sed 's/^small-//')"
done

echo "完成。模型文件："
ls -la "$DEST"
echo ""
echo "运行时路径：main.dart 用 getApplicationDocumentsDirectory()/whisper-small"
echo "macOS 需把 DEST 内容拷到 ~/Library/Containers/com.kite.kiteMobile/Data/Documents/whisper-small/"
