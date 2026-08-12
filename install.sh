#!/usr/bin/env bash
# 將 agent-team-kit 安裝到目標專案。
# 用法：./install.sh <目標專案路徑> [--force]
#
# kit/ 底下的結構就是目標專案的結構，安裝＝原封不動複製，不做任何改名。
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/kit"
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

echo "📦 安裝 agent-team-kit → $TARGET"

# 逐檔複製，預設保留目標端既有檔案（不用 cp -n，各平台行為不一致）
( cd "$KIT_ROOT" && find . -type f -print0 ) | while IFS= read -r -d '' rel; do
  rel="${rel#./}"
  if [ -e "$TARGET/$rel" ] && [ "$FORCE" != "--force" ]; then
    echo "  ⏭  略過既有檔案：$rel"
    continue
  fi
  mkdir -p "$TARGET/$(dirname "$rel")"
  cp "$KIT_ROOT/$rel" "$TARGET/$rel"
done

chmod +x "$TARGET"/.agent/scripts/*.py 2>/dev/null || true

cat <<EOF

✅ 安裝完成。接下來：

  1. 編輯 .agent/resources/team_protocol.md §3.1 模組前綴對照表，換成你的模組
  2. 依 docs/features/_TEMPLATE/ 複製出第一個功能模組目錄
  3. 依 CLAUDE.md 模板填寫專案的入口摘要
  4. 驗證腳本（需先完成第 2 步——沒有任何功能模組時腳本會提示找不到工單）：
     python .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md

EOF
