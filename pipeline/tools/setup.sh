#!/usr/bin/env bash
# Prepara o ambiente de render (rodar 1x por sessão nova)
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
python3 -c "import cairo, numpy" 2>/dev/null || pip install --break-system-packages -q pycairo numpy
mkdir -p ~/.fonts && cp "$HERE/fonts/"*.ttf ~/.fonts/ && (fc-cache -f >/dev/null 2>&1 || true)
which ffmpeg >/dev/null || (apt-get install -y -qq ffmpeg >/dev/null)
echo "export PYTHONPATH=$HERE/lib:\$PYTHONPATH"
echo "setup ok"
