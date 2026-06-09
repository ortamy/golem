# tools/generators/sync-changelogs.py — объединение CHANGELOG в один файл
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from lib.utils import read_file_safe, print_header, print_success, print_warning, print_hint, REPO_ROOT

GLOBAL_CHANGELOG = REPO_ROOT / "docs" / "CHANGELOG.md"
LOCAL_CHANGELOG = REPO_ROOT / "tools" / "CHANGELOG.md"


def parse_entries(content: str) -> dict:
    entries = {}
    pattern = re.compile(r'(##\s+\[.*?\].*?)(?=\n##\s+\[|\Z)', re.DOTALL)
    for match in pattern.finditer(content):
        block = match.group(1).strip()
        header = re.search(r'##\s+\[(.*?)\]\s*-\s*(\d{4}-\d{2}-\d{2})', block)
        if header:
            version = header.group(1)
            date = header.group(2)
            entries[version] = {"date": date, "block": block}
    return entries


def parse_local_entries(content: str) -> dict:
    entries = {}
    pattern = re.compile(r'(##\s+\[(.*?)\]\s*-\s*(\d{4}-\d{2}-\d{2})\n\n###\s+(.*?)\n(.*?))(?=\n##\s+\[|\Z)', re.DOTALL)
    for match in pattern.finditer(content):
        version = match.group(2)
        date = match.group(3)
        changes_block = match.group(1).strip()
        changes = re.findall(r'-\s+(.+?)(?=\n-|\n\n|\Z)', changes_block, re.DOTALL)
        changes = [c.strip() for c in changes if c.strip()]
        if version not in entries:
            entries[version] = {"date": date, "changes": []}
        entries[version]["changes"].extend(changes)
    return entries


def merge():
    global_content = read_file_safe(GLOBAL_CHANGELOG) or ""
    local_content = read_file_safe(LOCAL_CHANGELOG) or ""
    global_entries = parse_entries(global_content)
    local_entries = parse_local_entries(local_content)
    if not local_entries:
        return None

    for version, local_data in local_entries.items():
        if version in global_entries:
            block = global_entries[version]["block"]
            tools_block = "\n### Инструменты\n\n" + "\n".join(f"- {c}" for c in local_data["changes"])
            if "### Инструменты" in block:
                block = re.sub(r'### Инструменты\n.*?(?=\n###|\n##|\Z)', tools_block, block, flags=re.DOTALL)
            else:
                block += f"\n{tools_block}\n"
            global_entries[version]["block"] = block
        else:
            date = local_data["date"]
            changes = "\n".join(f"- {c}" for c in local_data["changes"])
            block = f"## [{version}] - {date}\n\n### Инструменты\n\n{changes}\n"
            global_entries[version] = {"date": date, "block": block}

    sorted_versions = sorted(global_entries.keys(),
                             key=lambda v: [int(x) for x in v.split('.') if x.isdigit()],
                             reverse=True)
    preamble = re.split(r'\n##\s+\[', global_content, maxsplit=1)[0] if '## [' in global_content else ""
    if not preamble and global_content:
        preamble = global_content

    lines = []
    if preamble and '## [' not in preamble:
        lines.append(preamble.strip())
        lines.append("")

    for version in sorted_versions:
        lines.append(global_entries[version]["block"])
        lines.append("")

    return '\n'.join(lines).strip() + '\n'


def main():
    print_header("ОБЪЕДИНЕНИЕ CHANGELOG", "📝")
    if not LOCAL_CHANGELOG.exists():
        print_warning("tools/CHANGELOG.md не найден")
        return 0
    if not GLOBAL_CHANGELOG.exists():
        print_warning("docs/CHANGELOG.md не найден")
        return 1

    local_content = read_file_safe(LOCAL_CHANGELOG) or ""
    local_entries = parse_local_entries(local_content)
    print(f"Локальных записей: {len(local_entries)}")
    total_changes = sum(len(e["changes"]) for e in local_entries.values())
    print(f"Локальных изменений: {total_changes}")

    merged = merge()
    if merged:
        with open(GLOBAL_CHANGELOG, 'w', encoding='utf-8') as f:
            f.write(merged)
        print_success(f"CHANGELOG объединён: {GLOBAL_CHANGELOG}")
        print(f"   Записей: {len(parse_entries(merged))}")
        print_hint("Локальный CHANGELOG можно очистить или удалить")
    else:
        print_warning("Не удалось объединить")
    return 0


if __name__ == "__main__":
    sys.exit(main())