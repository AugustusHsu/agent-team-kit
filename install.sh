#!/usr/bin/env bash
# 將 agent-team-kit 安裝到目標專案，或把既有安裝升級到新版。
#
# 用法：
#   ./install.sh <目標專案路徑>                           首次安裝（既有檔案一律保留）
#   ./install.sh <目標專案路徑> --upgrade                 升級（只覆蓋使用者沒改過的檔案）
#   ./install.sh <目標專案路徑> --upgrade --dry-run       只報告會怎麼做，不寫入
#   ./install.sh <目標專案路徑> --force                   全部覆蓋（會蓋掉專案客製內容）
#
# kit/ 底下的結構就是目標專案的結構，安裝＝原封不動複製，不做任何改名。
set -euo pipefail

KIT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/kit"

# 安裝時記錄每個檔案的 sha256，升級時靠它區分「使用者改過」與「還是原版」。
# 沒有這份基準線就無法安全升級——只能在「全部不動」與「全部蓋掉」之間二選一。
MANIFEST_REL=".agent/.kit-manifest"

usage() {
  cat >&2 <<'USAGE'
用法：install.sh <目標專案路徑> [--upgrade [--dry-run] | --force]

  （不加旗標）  首次安裝：只補上缺少的檔案，既有檔案一律保留
  --upgrade     升級：使用者沒改過的檔案更新到新版；改過的另存 .new 供人工合併
  --dry-run     搭配 --upgrade，只印出會做什麼，不實際寫入
  --force       全部覆蓋，包含專案客製過的內容（危險，僅供重置用）
USAGE
}

TARGET=""
MODE="install"
DRY_RUN="no"

while [ $# -gt 0 ]; do
  case "$1" in
    --upgrade) MODE="upgrade" ;;
    --force) MODE="force" ;;
    --dry-run) DRY_RUN="yes" ;;
    -h | --help)
      usage
      exit 0
      ;;
    -*)
      echo "❌ 未知的選項：$1" >&2
      usage
      exit 1
      ;;
    *)
      if [ -n "$TARGET" ]; then
        echo "❌ 只能指定一個目標路徑" >&2
        usage
        exit 1
      fi
      TARGET="$1"
      ;;
  esac
  shift
done

if [ -z "$TARGET" ]; then
  usage
  exit 1
fi
if [ ! -d "$TARGET" ]; then
  echo "❌ 目標目錄不存在：$TARGET" >&2
  exit 1
fi
TARGET="$(cd "$TARGET" && pwd)"

if [ "$DRY_RUN" = "yes" ] && [ "$MODE" != "upgrade" ]; then
  echo "❌ --dry-run 只能搭配 --upgrade 使用" >&2
  exit 1
fi

# 種子檔：kit 給的只是起始內容，安裝後由專案自己接手。
# 升級時一律不動它們；新版新增的種子檔也不直接補進舊專案，改提示 migrate。
# 否則會洗掉專案的入口、自訂忽略規則與 BACKLOG，或在未遷移前改變 agent 行為。
is_seed_file() {
  case "$1" in
    AGENTS.md | CLAUDE.md | .gitignore | docs/development/BACKLOG.md | docs/development/overlap_zones.md | docs/features/README.md) return 0 ;;
    *) return 1 ;;
  esac
}

file_hash() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d' ' -f1
  else
    shasum -a 256 "$1" | cut -d' ' -f1
  fi
}

# 逐檔複製，預設保留目標端既有檔案（不用 cp -n，各平台行為不一致）
# 排除本機產生物：kit/ 是工作區，跑過測試就會留下 __pycache__，不該跟著裝進使用者專案
list_kit_files() {
  (cd "$KIT_ROOT" && find . \( -name __pycache__ -o -name .pytest_cache \) -prune -o \
    -type f ! -name '*.py[cod]' ! -name .DS_Store -print) | sed 's|^\./||' | LC_ALL=C sort
}

baseline_hash() {
  # 從既有 manifest 取出該檔在「上次安裝時」的 kit 版本雜湊；查無則回空字串
  [ -f "$TARGET/$MANIFEST_REL" ] || return 0
  awk -v want="$1" '$2 == want { print $1; exit }' "$TARGET/$MANIFEST_REL"
}

n_added=0
n_updated=0
n_current=0
n_kept=0
conflicts=()
MANIFEST_TMP="$(mktemp)"
trap 'rm -f "$MANIFEST_TMP"' EXIT

case "$MODE" in
  upgrade) echo "🔄 升級 agent-team-kit → $TARGET" ;;
  force)
    echo "⚠️  --force：既有檔案將被覆蓋"
    echo "📦 安裝 agent-team-kit → $TARGET"
    ;;
  *) echo "📦 安裝 agent-team-kit → $TARGET" ;;
esac
[ "$DRY_RUN" = "yes" ] && echo "   （--dry-run：不會寫入任何檔案）"

install_file() {
  [ "$DRY_RUN" = "yes" ] && return 0
  mkdir -p "$TARGET/$(dirname "$1")"
  cp "$KIT_ROOT/$1" "$TARGET/$1"
}

record() {
  # $1=雜湊 $2=相對路徑；空雜湊代表這次無從判定基準線，留待下次
  [ -n "$1" ] && printf '%s  %s\n' "$1" "$2" >>"$MANIFEST_TMP"
  return 0
}

while IFS= read -r rel; do
  kit_hash="$(file_hash "$KIT_ROOT/$rel")"

  # 升級舊專案時不直接補「新出現的種子檔」。種子檔由專案接手，新增入口尤其可能
  # 立即改變 agent 行為；最新版骨架已在 .agent/templates/，交給 migrate 產生候選。
  if [ ! -e "$TARGET/$rel" ]; then
    if [ "$MODE" = "upgrade" ] && is_seed_file "$rel"; then
      echo "  🌱 缺少種子檔，請執行 migrate：$rel"
      n_kept=$((n_kept + 1))
      continue
    fi
    install_file "$rel"
    n_added=$((n_added + 1))
    [ "$MODE" = "upgrade" ] && echo "  ➕ 新增：$rel"
    record "$kit_hash" "$rel"
    continue
  fi

  case "$MODE" in
    install)
      echo "  ⏭  略過既有檔案：$rel"
      n_kept=$((n_kept + 1))
      # 內容可能已被改過，基準線沿用舊值；沒有舊值就不記
      record "$(baseline_hash "$rel")" "$rel"
      ;;

    force)
      install_file "$rel"
      n_updated=$((n_updated + 1))
      record "$kit_hash" "$rel"
      ;;

    upgrade)
      if is_seed_file "$rel"; then
        echo "  🌱 保留種子檔（由專案自行維護）：$rel"
        n_kept=$((n_kept + 1))
        record "$(baseline_hash "$rel")" "$rel"
        continue
      fi

      current_hash="$(file_hash "$TARGET/$rel")"
      if [ "$current_hash" = "$kit_hash" ]; then
        n_current=$((n_current + 1))
        record "$kit_hash" "$rel"
        continue
      fi

      old_hash="$(baseline_hash "$rel")"
      if [ -n "$old_hash" ] && [ "$old_hash" = "$current_hash" ]; then
        # 目標端還是上次裝進去的原版，沒被動過 → 可安全覆蓋
        install_file "$rel"
        n_updated=$((n_updated + 1))
        echo "  ⬆️  更新：$rel"
        record "$kit_hash" "$rel"
      else
        # 使用者改過，或這次升級前根本沒有基準線（舊版安裝）→ 一律不覆蓋
        [ "$DRY_RUN" = "no" ] && cp "$KIT_ROOT/$rel" "$TARGET/$rel.new"
        conflicts+=("$rel")
        echo "  ⚠️  已改過，另存待合併：$rel.new"
        record "$old_hash" "$rel"
      fi
      ;;
  esac
done < <(list_kit_files)

if [ "$DRY_RUN" = "no" ]; then
  mkdir -p "$TARGET/$(dirname "$MANIFEST_REL")"
  {
    echo "# agent-team-kit 安裝基準線——記錄每個檔案「裝進來時」的 sha256。"
    echo "# 升級靠它區分使用者改過與否，請納入版控，不要手改。"
    LC_ALL=C sort -k2 "$MANIFEST_TMP"
  } >"$TARGET/$MANIFEST_REL"
  chmod +x "$TARGET"/.agent/scripts/*.py 2>/dev/null || true
fi

if [ "$MODE" = "upgrade" ]; then
  echo
  echo "── 升級摘要 ──"
  echo "  新增 $n_added、更新 $n_updated、已是最新 $n_current、保留 $n_kept、待合併 ${#conflicts[@]}"
  if [ ${#conflicts[@]} -gt 0 ]; then
    echo
    echo "⚠️  以下檔案你改過，新版另存為 .new，請自行比對合併後刪除 .new："
    for c in "${conflicts[@]}"; do
      echo "    diff -u $c $c.new"
    done
    echo
    echo "   其中 .agent/resources/team_protocol.md 通常只需要把新章節搬進去，"
    echo "   §3.1 的模組前綴表保留你自己的即可。"
  fi
  if [ "$DRY_RUN" = "yes" ]; then
    echo
    echo "（--dry-run：以上都沒有實際寫入）"
  fi
  exit 0
fi

cat <<EOF

✅ 安裝完成。接下來：

  1. 編輯 .agent/resources/team_protocol.md §3.1 模組前綴對照表，換成你的模組
  2. 依 docs/features/_TEMPLATE/ 複製出第一個功能模組目錄
  3. 初始化 Claude／Codex 入口與本機 execution profiles：
     python3 .agent/scripts/agent_runtime.py init
  4. 驗證腳本（需先完成第 2 步——沒有任何功能模組時腳本會提示找不到工單）：
     python .agent/scripts/scan_backlog.py --format backlog --output docs/development/BACKLOG.md

  日後要拿到 kit 的新版流程規範，跑：
     ./install.sh <本專案路徑> --upgrade --dry-run    # 先看會動到什麼
     ./install.sh <本專案路徑> --upgrade

EOF
