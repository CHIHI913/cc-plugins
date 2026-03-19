#!/usr/bin/env python3
"""Parse SWOT Analysis Markdown into JSON for Miro placement.

Usage: python swot_parser.py INPUT_MD [OUTPUT_JSON]

Detects S/W/O/T sections and cross-SWOT strategies by ### headings.
Items in SWOT matrix are used to highlight matching items in S/W/O/T sections.
"""

import json, re, sys

SECTION_MAP = {
    "S": "strengths",
    "W": "weaknesses",
    "O": "opportunities",
    "T": "threats",
}

CROSS_SECTIONS = {
    "積極戦略": "so_strategy",
    "改善戦略": "wo_strategy",
    "差別化戦略": "st_strategy",
    "防衛戦略": "wt_strategy",
}

ANCHOR_MAP = {
    "強み": "strengths",
    "弱み": "weaknesses",
    "機会": "opportunities",
    "脅威": "threats",
    "Strengths": "strengths",
    "Weaknesses": "weaknesses",
    "Opportunities": "opportunities",
    "Threats": "threats",
    "積極戦略": "so_strategy",
    "改善戦略": "wo_strategy",
    "差別化戦略": "st_strategy",
    "防衛戦略": "wt_strategy",
}


def detect_section(text):
    """Detect section from ### heading."""
    clean = text.strip().lstrip("#").strip()
    # S/W/O/T sections: "S（強み）" etc.
    m = re.match(r'([SWOT])[\s（(]', clean)
    if m:
        return SECTION_MAP.get(m.group(1))
    # Cross-SWOT sections
    for keyword, key in CROSS_SECTIONS.items():
        if keyword in clean:
            return key
    return None


def detect_h2(text):
    """Detect ## heading type."""
    clean = text.strip().lstrip("#").strip()
    if "マトリクス" in clean:
        return "matrix"
    if "クロスSWOT" in clean:
        return "cross"
    if "示唆" in clean:
        return "insights"
    return None


def is_separator(row_text):
    return bool(re.match(r'^\s*\|[\s\-:]+\|', row_text))


def parse_table_row(row_text):
    return [c.strip() for c in row_text.strip().strip("|").split("|")]


def extract_matrix_items(text):
    """Extract item names from SWOT matrix cell like 'S: キャリア支援の質、AI×人...'"""
    # Remove bold markers and S:/W:/O:/T: prefix
    clean = re.sub(r'\*\*', '', text).strip()
    clean = re.sub(r'^[SWOT]:\s*', '', clean)
    return [item.strip() for item in clean.split("、") if item.strip()]


def parse_md(text):
    lines = text.split("\n")
    title = ""
    sections = {}
    highlight_items = set()
    current_h2 = None
    current_section = None
    in_table = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("# ") and not stripped.startswith("## ") and not title:
            title = stripped.lstrip("#").strip()
            continue

        # ## headings
        if stripped.startswith("## ") and not stripped.startswith("### "):
            current_h2 = detect_h2(stripped)
            current_section = None
            in_table = False
            continue

        # ### headings
        if stripped.startswith("### "):
            sec = detect_section(stripped)
            if sec:
                current_section = sec
                current_h2 = None  # Exit matrix mode when entering S/W/O/T subsections
                if sec not in sections:
                    sections[sec] = []
            in_table = False
            continue

        # Matrix table - extract highlight items
        if current_h2 == "matrix" and current_section is None and stripped.startswith("|"):
            if is_separator(stripped):
                continue
            cells = parse_table_row(stripped)
            for cell in cells:
                if re.match(r'\*\*[SWOT]:', cell.strip()):
                    items = extract_matrix_items(cell)
                    highlight_items.update(items)
            continue

        if current_section is None:
            continue

        # Table processing
        if stripped.startswith("|"):
            if is_separator(stripped):
                continue
            cells = parse_table_row(stripped)
            if not in_table:
                in_table = True
                continue
            # S/W/O/T: col1=#, col2=要因, col3=裏付け
            if current_section in SECTION_MAP.values() and len(cells) >= 3:
                factor = cells[1].strip()
                evidence = cells[2].strip()
                if factor:
                    content = f"{factor}: {evidence}" if evidence else factor
                    highlight = any(h in factor for h in highlight_items)
                    sections[current_section].append({
                        "content": content,
                        "highlight": highlight,
                    })
            # Cross-SWOT: col1=#, col2=戦略
            elif current_section in CROSS_SECTIONS.values() and len(cells) >= 2:
                strategy = cells[1].strip()
                if strategy:
                    sections[current_section].append({
                        "content": strategy,
                        "highlight": False,
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
        print("Usage: python swot_parser.py INPUT_MD [OUTPUT_JSON]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()

    result = parse_md(text)

    print(f"\n=== SWOT Parse Result ===", file=sys.stderr)
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
