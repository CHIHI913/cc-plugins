#!/usr/bin/env python3
"""Parse PEST Analysis Markdown into JSON for Miro placement.

Usage: python pest_parser.py INPUT_MD [OUTPUT_JSON]

Detects P/E/S/T sections by ## heading keywords.
Each table row becomes: {"content": "要因: プロダクトへの示唆", "highlight": bool}
Items matching PEST要因評価 factors are highlighted (light_pink).
"""

import json, re, sys

SECTION_MAP = {
    "P": "politics",
    "E": "economy",
    "S": "society",
    "T": "technology",
}

ANCHOR_MAP = {
    "政治": "politics",
    "経済": "economy",
    "社会": "society",
    "技術": "technology",
    "Political": "politics",
    "Economic": "economy",
    "Social": "society",
    "Technological": "technology",
}


def detect_section(text):
    """Detect PEST section from ## heading."""
    clean = text.strip().lstrip("#").strip()
    m = re.match(r'([PEST])[\s（(]', clean)
    if m:
        return SECTION_MAP.get(m.group(1))
    if "サマリー" in clean:
        return "summary"
    if "要因評価" in clean or "PEST" in clean:
        return "evaluation"
    return None


def is_separator(row_text):
    return bool(re.match(r'^\s*\|[\s\-:]+\|', row_text))


def parse_table_row(row_text):
    return [c.strip() for c in row_text.strip().strip("|").split("|")]


def parse_md(text):
    lines = text.split("\n")
    title = ""
    sections = {"politics": [], "economy": [], "society": [], "technology": []}
    highlight_factors = set()
    current_section = None
    in_table = False

    # First pass: collect highlight factors from 要因評価
    temp_section = None
    temp_in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            sec = detect_section(stripped)
            temp_section = sec
            temp_in_table = False
            continue
        if temp_section == "evaluation" and stripped.startswith("|"):
            if is_separator(stripped):
                continue
            cells = parse_table_row(stripped)
            if not temp_in_table:
                temp_in_table = True
                continue
            # 要因列 (col index 2: after # and カテゴリ)
            if len(cells) >= 3:
                factor = cells[2].strip()
                if factor:
                    highlight_factors.add(factor)

    # Second pass: parse P/E/S/T sections
    current_section = None
    in_table = False
    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# ") and not stripped.startswith("## ") and not title:
            title = stripped.lstrip("#").strip()
            continue

        if stripped.startswith("## ") and not stripped.startswith("### "):
            sec = detect_section(stripped)
            current_section = sec if sec in sections else None
            in_table = False
            continue

        if current_section is None:
            continue

        if stripped.startswith("|"):
            if is_separator(stripped):
                continue
            cells = parse_table_row(stripped)
            if not in_table:
                in_table = True
                continue
            # Data row: combine 要因 + プロダクトへの示唆
            if len(cells) >= 4:
                factor = cells[1].strip()
                insight = cells[3].strip() if len(cells) > 3 else ""
                if factor:
                    content = f"{factor}: {insight}" if insight else factor
                    highlight = factor in highlight_factors
                    sections[current_section].append({
                        "content": content,
                        "highlight": highlight,
                    })
            elif len(cells) >= 2:
                factor = cells[1].strip()
                if factor:
                    highlight = factor in highlight_factors
                    sections[current_section].append({
                        "content": factor,
                        "highlight": highlight,
                    })
            continue

        if in_table and stripped:
            in_table = False

    result = {
        "title": title,
        "sections": sections,
        "anchor_map": ANCHOR_MAP,
    }

    total = sum(len(v) for v in sections.values())
    n_highlight = sum(1 for v in sections.values() for i in v if i.get("highlight"))
    result["stats"] = {k: len(v) for k, v in sections.items()}
    result["stats"]["total"] = total
    result["stats"]["highlighted"] = n_highlight

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python pest_parser.py INPUT_MD [OUTPUT_JSON]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()

    result = parse_md(text)

    print(f"\n=== PEST Parse Result ===", file=sys.stderr)
    print(f"Title: {result['title']}", file=sys.stderr)
    s = result["stats"]
    print(f"Total: {s['total']} items ({s['highlighted']} highlighted)\n", file=sys.stderr)

    for key, items in result["sections"].items():
        if items:
            hl = sum(1 for i in items if i.get("highlight"))
            print(f"  {key}: {len(items)}件 ({hl} highlighted)", file=sys.stderr)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nWritten to {sys.argv[2]}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
