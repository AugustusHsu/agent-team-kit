#!/usr/bin/env python3
"""
第三方映像檔與工具鏈版本檢查腳本 (check_versions.py)

功能：
  1. 讀取 docs/standards/third_party_versions.yaml 清單。
  2. 【自我驗證】驗證清單中的 current_version 與 declared_in.pattern 是否真實存在於指定檔案中。
  3. 【一致性驗證】校驗關聯項目（如 cypress image 與 npm）版本號是否一致。
  4. 【上游查詢】向 DockerHub, PyPI, npm, GitHub API 查詢最新版本。
  5. 格式化輸出對照表並依狀況回傳 Exit Code。
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path


def parse_yaml_fallback(text: str) -> dict:
    """極簡 YAML 解析備用方案 (當無 PyYAML 時適用)"""
    versions = []
    current_entry = None
    current_section = None

    for line in text.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("#"):
            continue

        if line_str.startswith("- name:"):
            if current_entry:
                versions.append(current_entry)
            current_entry = {"name": line_str.split(":", 1)[1].strip().strip('"\'')}
            current_section = None
            continue

        if current_entry is not None:
            if line_str.startswith("declared_in:"):
                current_entry["declared_in"] = {}
                current_section = "declared_in"
                continue

            if ":" in line_str:
                k, v = line_str.split(":", 1)
                k = k.strip("- ").strip()
                v = v.strip().strip('"\'')

                if current_section == "declared_in":
                    current_entry["declared_in"][k] = v
                else:
                    current_entry[k] = v

    if current_entry:
        versions.append(current_entry)

    return {"versions": versions}


def load_manifest(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        return parse_yaml_fallback(text)


def find_repo_root() -> Path:
    """尋找專案根目錄 (含 Makefile 或 .git 的目錄)"""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "Makefile").exists() or (current / ".git").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def fetch_json(url: str, headers: dict = None, timeout: int = 5):
    """發送 HTTP GET 請求並解析 JSON (帶逾時防護)"""
    req = urllib.request.Request(url, headers=headers or {})
    req.add_header("User-Agent", "my-workstation-version-checker/1.0")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            if response.status == 200:
                return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    return None


def get_latest_dockerhub(repository: str, tag_prefix: str = None, tag_suffix: str = None) -> str:
    """自 DockerHub API 查詢最新 tag (支援分頁與變體過濾)"""
    name_filter = f"&name={tag_prefix.rstrip('.')}" if tag_prefix else ""
    url = f"https://hub.docker.com/v2/repositories/{repository}/tags?page_size=100{name_filter}"
    matching_tags = []

    # 遍歷最多 5 頁，避免多版本 tag 頁數不足 (如 library/node)
    for _ in range(5):
        if not url:
            break
        data = fetch_json(url)
        if not data or "results" not in data:
            break

        for item in data["results"]:
            name = item["name"]
            if re.search(r"latest|nightly|main|master", name, re.I):
                continue
            if tag_prefix and not name.startswith(tag_prefix):
                continue
            if tag_suffix and not name.endswith(tag_suffix):
                continue
            if not tag_suffix or "cpuv1" not in tag_suffix:
                if "-cpuv1" in name or "-arm" in name:
                    continue
            matching_tags.append(name)

        if matching_tags:
            break
        url = data.get("next")

    if matching_tags:
        return matching_tags[0]
    return "UNKNOWN"


def get_latest_pypi(package: str) -> str:
    """自 PyPI API 查詢最新版本"""
    url = f"https://pypi.org/pypi/{package}/json"
    data = fetch_json(url)
    if data and "info" in data and "version" in data["info"]:
        return data["info"]["version"]
    return "FETCH FAILED"


def get_latest_npm(package: str) -> str:
    """自 npm Registry 查詢最新版本"""
    url = f"https://registry.npmjs.org/{package}/latest"
    data = fetch_json(url)
    if data and "version" in data:
        return data["version"]
    return "FETCH FAILED"


def get_latest_github(owner: str, repo: str) -> str:
    """自 GitHub API 查詢最新 release/tag"""
    url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    data = fetch_json(url)
    if data and "tag_name" in data:
        return data["tag_name"]

    url_tags = f"https://api.github.com/repos/{owner}/{repo}/tags"
    tags_data = fetch_json(url_tags)
    if tags_data and isinstance(tags_data, list) and len(tags_data) > 0:
        return tags_data[0]["name"]

    return "FETCH FAILED"


def check_upstream(entry: dict) -> str:
    """依據 source_type 發起對應的上游查詢"""
    source_type = entry.get("source_type")
    try:
        if source_type == "dockerhub":
            return get_latest_dockerhub(
                entry["repository"],
                entry.get("tag_prefix"),
                entry.get("tag_suffix"),
            )
        elif source_type == "pypi":
            return get_latest_pypi(entry["package"])
        elif source_type == "npm":
            return get_latest_npm(entry["package"])
        elif source_type == "github-tag":
            return get_latest_github(entry["owner"], entry["repo"])
        else:
            return "UNSUPPORTED SOURCE"
    except Exception as e:
        return f"FETCH FAILED ({str(e)})"


def main():
    parser = argparse.ArgumentParser(description="第三方依賴與版本宣告檢查工具")
    parser.add_argument(
        "--config",
        default="docs/standards/third_party_versions.yaml",
        help="宣告檔相對路徑",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    config_path = repo_root / args.config

    if not config_path.exists():
        print(f"❌ 找不到版本宣告檔：{config_path}")
        sys.exit(1)

    manifest = load_manifest(config_path)
    entries = manifest.get("versions", [])
    print(f"🔍 載入版本宣告檔：{args.config} (共 {len(entries)} 項依賴)\n")

    # 1. 自我驗證 (Self-validation) 與 一致性驗證
    self_val_passed = True
    entries_map = {e["name"]: e for e in entries}

    print("==================== [階段一：清單自我驗證] ====================")
    for entry in entries:
        name = entry["name"]
        curr_ver = entry.get("current_version", "")
        declared = entry.get("declared_in", {})
        rel_file = declared.get("file")
        pattern = declared.get("pattern")

        if not rel_file or not pattern:
            print(f"❌ [{name}] 缺少 declared_in 屬性")
            self_val_passed = False
            continue

        target_file = repo_root / rel_file
        if not target_file.exists():
            print(f"❌ [{name}] 指定宣告檔案不存在：{rel_file}")
            self_val_passed = False
            continue

        content = target_file.read_text(encoding="utf-8")

        # 替換 {version} 為 current_version 進行實體校驗，確保單一真源
        expected_pattern = pattern.replace("{version}", curr_ver) if "{version}" in pattern else pattern

        if expected_pattern not in content:
            print(f"❌ [{name}] 自我驗證失敗！預期模式 '{expected_pattern}' 不存在於檔案 '{rel_file}' 中。")
            self_val_passed = False
        else:
            consistency_with = entry.get("consistency_check_with")
            if consistency_with:
                other = entries_map.get(consistency_with)
                if not other or curr_ver != other.get("current_version"):
                    other_ver = other.get("current_version") if other else "N/A"
                    print(
                        f"❌ [{name}] 一致性驗證失敗！本版 ({curr_ver}) "
                        f"與 {consistency_with} ({other_ver}) 不一致！"
                    )
                    self_val_passed = False
                else:
                    print(f"✅ [{name}] 檔案模式與關聯一致性校驗 OK ({rel_file})")
            else:
                print(f"✅ [{name}] 檔案模式存在校驗 OK ({rel_file})")

    if not self_val_passed:
        print("\n💥 清單自我驗證失敗！請修復宣告清單與實體檔案不一致問題後再試。")
        sys.exit(1)

    print("\n==================== [階段二：上游版本巡檢] ====================")
    has_outdated = False
    has_failure = False
    results = []

    FAILURE_PREFIXES = ("FETCH FAILED", "UNSUPPORTED SOURCE", "UNKNOWN")

    for entry in entries:
        name = entry["name"]
        curr_ver = entry["current_version"]
        hold_reason = entry.get("hold_reason", "")

        print(f"📡 正在查詢 {name} ({entry['source_type']})...")
        latest_ver = check_upstream(entry)

        is_failed = any(latest_ver.startswith(p) for p in FAILURE_PREFIXES)
        is_outdated = False

        if is_failed:
            status_str = "❓ Unknown (查詢失敗)"
            has_failure = True
        else:
            if latest_ver != curr_ver:
                is_outdated = True
                if not hold_reason:
                    has_outdated = True

            if is_outdated:
                if hold_reason:
                    status_str = "⏸️ Held (Ignored)"
                else:
                    status_str = "⚠️ Outdated"
            else:
                status_str = "✅ Up-to-date"

        results.append({
            "name": name,
            "current": curr_ver,
            "latest": latest_ver,
            "status": status_str,
            "hold_reason": hold_reason,
        })

    print("\n" + "=" * 80)
    print(f"{'名稱 (Name)':<20} | {'目前版本 (Current)':<20} | {'最新版本 (Latest)':<20} | {'狀態 (Status)'}")
    print("-" * 80)
    for r in results:
        print(f"{r['name']:<20} | {r['current']:<20} | {r['latest']:<20} | {r['status']}")
        if r["hold_reason"]:
            print(f"  └ 📌 暫緩原因: {r['hold_reason']}")
    print("=" * 80 + "\n")

    if has_failure:
        print("❌ 注意：存在查詢失敗的第三方依賴項目，請檢查網路連線或 API 狀態。")
        sys.exit(1)
    elif has_outdated:
        print("⚠️ 注意：存在未暫緩的第三方落後依賴，請參考 devenv_spec.md 升級流程進行更新。")
        sys.exit(1)
    else:
        print("🎉 全部第三方依賴均為最新（或已於清單中適當暫緩）。")
        sys.exit(0)


if __name__ == "__main__":
    main()
