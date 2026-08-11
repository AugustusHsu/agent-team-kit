#!/usr/bin/env bash
# 將 agent-team-kit 安裝到目標專案。
# 用法：./scripts/install.sh <目標專案路徑> [--force]
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-}"
FORCE="${2:-}"

if [ -z "$TARGET" ]; then
  echo "用法：$0 <目標專案路徑> [--force]" >&2
  exit 1
fi
if [ ! -d "$TARGET" ]; then
  echo "❌ 目標目錄不存在：$TARGET" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"

if [ "$FORCE" = "--force" ]; then
  echo "⚠️  --force：既有檔案將被覆蓋"
fi

# 逐檔複製，預設保留目標端既有檔案（不用 cp -n，各平台行為不一致）
copy_tree() {
  local src="$1" dst="$2" rel
  ( cd "$src" && find . -type f -print0 ) | while IFS= read -r -d '' rel; do
    mkdir -p "$dst/$(dirname "$rel")"
    if [ -e "$dst/$rel" ] && [ "$FORCE" != "--force" ]; then
      echo "  ⏭  略過既有檔案：${dst#"$TARGET"/}/$rel"
      continue
    fi
    cp "$src/$rel" "$dst/$rel"
  done
}

echo "📦 安裝 agent-team-kit → $TARGET"

mkdir -p "$TARGET/.agent" "$TARGET/docs"
copy_tree "$KIT_ROOT/agent" "$TARGET/.agent"
copy_tree "$KIT_ROOT/docs-template" "$TARGET/docs"
chmod +x "$TARGET"/.agent/scripts/*.py 2>/dev/null || true

if [ ! -f "$TARGET/CLAUDE.md" ]; then
  cp "$KIT_ROOT/templates/CLAUDE.md" "$TARGET/CLAUDE.md"
  echo "  ✚ 已建立 CLAUDE.md（模板，請依專案填寫）"
else
  echo "  ⏭  CLAUDE.md 已存在，略過（模板在 $KIT_ROOT/templates/CLAUDE.md）"
fi

cat <<EOF

✅ 安裝完成。接下來：

  1. 編輯 .agent/resources/team_protocol.md §3.1 模組前綴對照表，換成你的模組
  2. 依 docs/features/_TEMPLATE/ 複製出第一個功能模組目錄
  3. 依 CLAUDE.md 模板填寫專案的入口摘要
  4. 驗證腳本：
     python .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md

EOF
