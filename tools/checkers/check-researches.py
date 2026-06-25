#!/usr/bin/env python3
"""
Checker for research files in content/researches/.
Checks integrity and conformity to TEMPLATE-RESEARCH.md template.

Usage:
  python check-researches.py
  python check-researches.py --dir content/researches
"""

import os
import re
import sys
import argparse
from collections import defaultdict

# Constants
ICONS_DIR = os.path.join("web", "icons", "32")

# Section patterns - using actual Russian text from the files
SECTION_PATTERNS = [
    (r"##\s.*ВВЕДЕНИЕ", "ВВЕДЕНИЕ"),
    (r"##\s.*РАЗОБЛАЧЕНИЕ", "РАЗОБЛАЧЕНИЕ"),
    (r"##\s.*СВОДКА", "СВОДКА"),
]

# Metadata field names as they appear in files (Russian)
REQUIRED_METADATA_FIELDS = ["Файл", "Версия", "Статус", "Тема"]
ALL_METADATA_FIELDS = [
    "Файл", "Версия", "Дата создания", "Последнее обновление",
    "Причина обновления", "Статус", "Тема", "Аудит",
    "Язык", "Связанные файлы", "Хеш", "Достоверность",
    "Последний аудит", "Уровень",
]

# Placeholder patterns - using actual Russian text
PLACEHOLDER_PATTERNS = [
    r"ПОДМЕНА:\s*\.\.\.\s*ЗАМЕНЁН",
    r"ПОДМЕНА:\s*\.\.\.",
    r"→\s*\.{3,}",
    r"\.\.\.\s*—\s*\.\.\.",
]

# Existing icons cache
EXISTING_ICONS = None


def load_existing_icons():
    """Load list of actually existing icon files."""
    global EXISTING_ICONS
    if EXISTING_ICONS is not None:
        return EXISTING_ICONS
    if not os.path.isdir(ICONS_DIR):
        EXISTING_ICONS = set()
        return EXISTING_ICONS
    EXISTING_ICONS = set(os.listdir(ICONS_DIR))
    return EXISTING_ICONS


def find_md_files(root_dir):
    """Find all .md files recursively."""
    md_files = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for filename in filenames:
            if filename.endswith('.md'):
                md_files.append(os.path.join(dirpath, filename))
    return sorted(md_files)


def check_ellipsis(text):
    """Count ellipsis occurrences."""
    return len(re.findall(r'\.\.\.', text))


def check_arrows(text):
    """Count arrow occurrences."""
    return len(re.findall(r'→', text))


def check_placeholders(text):
    """Check for unfilled placeholders."""
    issues = []
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            issues.append(f"unfilled placeholder: {pattern}")
    return issues


def check_icon_path(text):
    """Check if icon file referenced in header exists."""
    existing = load_existing_icons()
    # Check first 5 lines for icon reference
    first_lines = "\n".join(text.split('\n')[:5])
    match = re.search(r'!\[icon\]\(icons/32/([^)]+)\)', first_lines)
    if not match:
        return {"has_icon": False, "icon_file": None, "exists": None}
    icon_file = match.group(1)
    exists = icon_file in existing
    return {"has_icon": True, "icon_file": icon_file, "exists": exists}


def check_sections(text):
    """Check presence of required sections."""
    found = {}
    for pattern, name in SECTION_PATTERNS:
        found[name] = bool(re.search(pattern, text))
    return found


def check_metadata(text):
    """Check metadata fields."""
    metadata = {}
    pattern = r'-\s+\*\*([^*]+)\*\*:\s*(.*)'
    for match in re.finditer(pattern, text):
        field = match.group(1).strip()
        value = match.group(2).strip()
        metadata[field] = value

    found_required = {}
    for field in REQUIRED_METADATA_FIELDS:
        found_required[field] = field in metadata and bool(metadata[field])

    total_fields = len(metadata)
    return {
        "all_fields": metadata,
        "found_required": found_required,
        "total_fields": total_fields,
        "missing_all": [f for f in ALL_METADATA_FIELDS if f not in metadata],
    }


def check_file(filepath):
    """Check a single .md file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"filepath": filepath, "error": str(e), "issues": []}

    issues = []
    severity = "OK"

    # 1. Ellipsis
    ellipsis_count = check_ellipsis(content)
    if ellipsis_count > 2:
        issues.append(f"NOT FINISHED: {ellipsis_count} ellipses (more than 2)")
        severity = "NOT FINISHED"

    # 2. Arrows
    arrow_count = check_arrows(content)
    if arrow_count > 0:
        issues.append(f"BROKEN GLOSSARY INSERT: {arrow_count} arrows found")
        if severity == "OK":
            severity = "BROKEN GLOSSARY"

    # 3. Placeholders
    placeholders = check_placeholders(content)
    for ph in placeholders:
        issues.append(f"PLACEHOLDER: {ph}")
        if severity == "OK":
            severity = "PLACEHOLDER"

    # 4. Icon
    icon_info = check_icon_path(content)
    if icon_info["has_icon"] and not icon_info["exists"]:
        issues.append(f"ICON NOT FOUND: icons/32/{icon_info['icon_file']}")
        if severity == "OK":
            severity = "ICON MISSING"

    # 5. Sections
    sections = check_sections(content)
    missing_sections = [s for s, found in sections.items() if not found]
    if missing_sections:
        issues.append(f"MISSING SECTIONS: {', '.join(missing_sections)}")
        if severity == "OK":
            severity = "MISSING SECTIONS"

    # 6. Metadata
    meta = check_metadata(content)
    missing_required = [f for f, v in meta["found_required"].items() if not v]
    if missing_required:
        issues.append(f"MISSING METADATA: {', '.join(missing_required)}")
        if severity == "OK":
            severity = "MISSING METADATA"

    if meta["total_fields"] < 4:
        issues.append(f"METADATA: only {meta['total_fields']} fields (need min 4 basic)")
        if severity == "OK":
            severity = "FEW METADATA"

    return {
        "filepath": filepath,
        "issues": issues,
        "severity": severity,
        "ellipsis_count": ellipsis_count,
        "arrow_count": arrow_count,
        "sections": sections,
        "metadata": meta,
        "icon_info": icon_info,
    }


def format_report(results):
    """Format the report."""
    total = len(results)
    errors = [r for r in results if "error" in r]
    ok_files = [r for r in results if not r.get("issues") and "error" not in r]
    problem_files = [r for r in results if r.get("issues") and "error" not in r]

    lines = []
    lines.append("=" * 70)
    lines.append("  REPORT: RESEARCH FILES CHECK - content/researches/")
    lines.append("=" * 70)
    lines.append(f"  Total files:                 {total}")
    lines.append(f"  OK (no issues):              {len(ok_files)}")
    lines.append(f"  With issues:                 {len(problem_files)}")
    lines.append(f"  Read errors:                 {len(errors)}")
    lines.append("")

    severity_counts = defaultdict(int)
    for r in problem_files:
        severity_counts[r["severity"]] += 1

    if severity_counts:
        lines.append("  PROBLEM STATISTICS:")
        for sev, count in sorted(severity_counts.items(), key=lambda x: -x[1]):
            lines.append(f"    {sev}: {count}")
        lines.append("")

    lines.append("-" * 70)
    lines.append("  DETAILED REPORT")
    lines.append("-" * 70)

    by_severity = defaultdict(list)
    for r in problem_files:
        by_severity[r["severity"]].append(r)

    sev_order = ["NOT FINISHED", "BROKEN GLOSSARY", "PLACEHOLDER",
                 "ICON MISSING", "MISSING SECTIONS", "MISSING METADATA",
                 "FEW METADATA"]

    for sev in sev_order:
        if sev in by_severity:
            lines.append(f"\n  [{sev}]")
            for r in sorted(by_severity[sev], key=lambda x: x["filepath"]):
                short_path = os.path.relpath(r["filepath"], "content/researches")
                for issue in r["issues"]:
                    lines.append(f"    [X] {short_path}: {issue}")
                if r["ellipsis_count"] > 0:
                    lines.append(f"       ...: {r['ellipsis_count']} times")
                if r["arrow_count"] > 0:
                    lines.append(f"       ->: {r['arrow_count']} times")
                missing = [s for s, f in r["sections"].items() if not f]
                if missing:
                    lines.append(f"       Sections missing: {missing}")
                if r["metadata"]["total_fields"] < 14:
                    lines.append(f"       Metadata: {r['metadata']['total_fields']}/14 fields")
                if r["icon_info"]["has_icon"] and not r["icon_info"]["exists"]:
                    lines.append(f"       Icon: {r['icon_info']['icon_file']} missing in web/icons/32/")

    if ok_files:
        lines.append(f"\n  [OK - no issues] ({len(ok_files)})")
        for r in sorted(ok_files, key=lambda x: x["filepath"]):
            short_path = os.path.relpath(r["filepath"], "content/researches")
            meta_count = r["metadata"]["total_fields"]
            icon_status = ""
            if r["icon_info"]["has_icon"]:
                icon_status = f" icon:{r['icon_info']['icon_file']}"
            lines.append(f"    [V] {short_path} (meta:{meta_count}/14{icon_status})")

    lines.append("")
    lines.append("=" * 70)
    lines.append("  LEGEND:")
    lines.append("    NOT FINISHED      - more than 2 ellipses (...) in text")
    lines.append("    BROKEN GLOSSARY   - arrows found (broken glossary insert)")
    lines.append("    PLACEHOLDER       - unfilled template (PODMENA: ...)")
    lines.append("    ICON MISSING      - icon in header not found in web/icons/32/")
    lines.append("    MISSING SECTIONS  - required sections missing")
    lines.append("    MISSING METADATA  - required metadata fields missing")
    lines.append("    FEW METADATA      - less than 4 metadata fields")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Check research files in content/researches/ for integrity'
    )
    parser.add_argument(
        '--dir', '-d',
        default='content/researches',
        help='Directory to check (default: content/researches)'
    )
    parser.add_argument(
        '--output', '-o',
        default='reports/researches-report.txt',
        help='Output file for report (default: reports/researches-report.txt)'
    )

    args = parser.parse_args()

    # Ensure output directory exists
    out_dir = os.path.dirname(args.output)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir)

    md_files = find_md_files(args.dir)

    if not md_files:
        msg = f"No .md files found in {args.dir}"
        print(msg)
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(msg + "\n")
        sys.exit(1)

    results = []
    for f in md_files:
        result = check_file(f)
        results.append(result)

    report = format_report(results)

    total_issues = sum(len(r["issues"]) for r in results)
    report += f"\n  Total issues: {total_issues}\n"

    # Write to file with UTF-8 encoding
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report written to: {args.output}")
    print(report)


if __name__ == '__main__':
    main()