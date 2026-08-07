#!/usr/bin/env bash
# 下载 whisper-small（sherpa-onnx 格式）端侧转写模型。
# 模型 ~200MB，不入库（.gitignore 排除 assets/models/）。
# DEC-CAP-TRANSCRIPTION 选 A 端侧 whisper-small。
#
# 用法：
#   ./apps/mobile/scripts/download-whisper-model.sh <目标目录>
#   默认下载到 apps/mobile/assets/models/whisper-small/
#
# 模型来自 k2-fsa/sherpa-onnx releases（sherpa-onnx-whisper-small.tar.bz2）。
set -euo pipefail

DEST="${1:-apps/mobile/assets/models/whisper-small}"
MODEL_URL="https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$DEST"
echo "下载 whisper-small 到 $TMP ..."
curl -L --retry 6 -o "$TMP/model.tar.bz2" "$MODEL_URL"
echo "解压..."
tar -xjf "$TMP/model.tar.bz2" -C "$TMP"
# 解压出 sherpa-onnx-whisper-small/ 目录，移文件到 DEST
SRC=$(find "$TMP" -maxdepth 1 -type d -name "sherpa-onnx-whisper-small*" | head -1)
cp "$SRC"/* "$DEST"/
echo "完成。模型文件："
ls "$DEST"
echo ""
echo "运行时路径：app 需把这些文件放到可读目录（macOS: app Documents；移动端: 复制 asset → Documents）"
echo "main.dart 的 WhisperTranscriber.init(modelDir) 指向该目录。"
