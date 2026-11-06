#!/usr/bin/env bash
# Usage: ./switch.sh homepage|manufacturing [--push]
# Copies designs/<name>.html to index.html (the live page on GitHub Pages).
set -euo pipefail
cd "$(dirname "$0")"

name="${1:-}"
if [[ ! -f "designs/$name.html" ]]; then
  echo "Usage: $0 <design> [--push]"
  echo "Available: $(ls designs | sed 's/\.html$//' | tr '\n' ' ')"
  exit 1
fi

cp "designs/$name.html" index.html
echo "index.html is now: $name"

if [[ "${2:-}" == "--push" ]]; then
  git add index.html
  git commit -m "Switch live design to $name"
  git push
fi
