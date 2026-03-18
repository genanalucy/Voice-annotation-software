#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

python3 -m pip install pyinstaller
rm -rf build dist

pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "语音标注软件" \
  --add-data "question_config.py:." \
  app.py

echo
echo "macOS 打包完成："
echo "App: $ROOT_DIR/dist/语音标注软件.app"

