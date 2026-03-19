#!/usr/bin/env python3
"""Parse Lean Canvas Markdown into JSON for Miro placement.

Usage: python lean_canvas_parser.py INPUT_MD [OUTPUT_JSON]

Sections detected by ## heading number (1-9).
Bullet points (- XXX) are extracted as items.
Table rows in 既存の代替品 are extracted as "課題: 直接競合 / 代替行動".
"""

import json, re, sys

# Section detection: heading number/keyword → section key
SECTION_MAP = {
    "1": "customer_segments",
    "2": "problems",
    "3": "uvp",
    "4": "solutions",
    "5": "channels",
    "6": "revenue",
    "7": "costs",
    "8": "key_metrics",
    "9": "unfair_advantage",
}

# Sub-section detection within ## sections
SUB_SECTIONS = {
    "カスタマーセグメント": "customer_segments",
    "アーリーアダプター": "early_adopters",
    "既存の代替品": "existing_alternatives",
    "UVP": "uvp_statement",
    "ハイレベルコンセプト": "high_level_concept",
    "NSM": "nsm",
    "KPI": "kpi",
}

# Miro anchor keyword → section key mapping
ANCHOR_MAP = {
    "課題": "problems",
    "既存の代替品": "existing_alternatives",
    "ソリューション": "solutions",
    "主要指標": "key_metrics",
    "主要指数": "key_metrics",
    "独自の価値提案": "uvp",
    "ハイレベルコンセプト": "high_level_concept",
    "圧倒的な優位性": "unfair_advantage",
    "チャネル": "channels",
    "カスタマーセグメント": "customer_segments",
    "アーリーアダプター": "early_adopters",
    "コスト構造": "costs",
    "収益の流れ": "revenue",
}


def detect_h2_section(text):
    """Detect section from ## heading."""
    clean = text.strip().lstrip("#").strip()
    # Match "1：カスタマーセグメント" pattern
    m = re.match(r'(\d+)[：:]', clean)
    if m:
        return SECTION_MAP.get(m.group(1))
    # Check for 検証チェックリスト (skip)
    if "検証" in clean or "チェックリスト" in clean:
        return "checklist"
    return None


def detect_h3_subsection(text):
    """Detect sub-section from ### heading."""
    clean = text.strip().lstrip("#").strip()
    for keyword, key in SUB_SECTIONS.items():
        if keyword in clean:
            return key
    return None


def parse_table_row(row_text):
    """Parse a table row into cells."""
    return [c.strip() for c in row_text.strip().strip("|").split("|")]


def is_separator(row_text):
    """Check if row is a table separator."""
    return bool(re.match(r'^\s*\|[\s\-:]+\|', row_text))


def parse_md(text):
    """Parse Lean Canvas Markdown into structured data."""
    lines = text.split("\n")
    title = ""
    sections = {}
    current_section = None
    current_subsection = None
    in_table = False
    table_headers = []

    for line in lines:
        stripped = line.strip()

        # Title
        if stripped.startswith("# ") and not stripped.startswith("## ") and not title:
            title = stripped.lstrip("#").strip()
            continue

        # ## section headers
        if stripped.startswith("## ") and not stripped.startswith("### "):
            sec = detect_h2_section(stripped)
            if sec:
                current_section = sec
                current_subsection = None
                if sec not in sections:
                    sections[sec] = []
            else:
                current_section = None
                current_subsection = None
            in_table = False
            continue

        # ### sub-section headers
        if stripped.startswith("### "):
            sub = detect_h3_subsection(stripped)
            if sub:
                current_subsection = sub
                if sub not in sections:
                    sections[sub] = []
            in_table = False
            continue

        if current_section is None and current_subsection is None:
            continue

        # Skip checklist section
        if current_section == "checklist":
            continue

        active_key = current_subsection or current_section

        # Table processing (既存の代替品)
        if stripped.startswith("|"):
            if is_separator(stripped):
                continue
            cells = parse_table_row(stripped)
            if not in_table:
                # Header row
                table_headers = cells
                in_table = True
                continue
            # Data row - combine into single string
            if len(cells) >= 2:
                parts = [c for c in cells if c]
                content = " / ".join(parts)
                if content:
                    if active_key not in sections:
                        sections[active_key] = []
                    sections[active_key].append(content)
            continue

        # Bullet points
        if stripped.startswith("- "):
            content = stripped[2:].strip()
            if content:
                if active_key not in sections:
                    sections[active_key] = []
                sections[active_key].append(content)
            in_table = False
            continue

        # Non-table, non-bullet → reset table mode
        if in_table and stripped:
            in_table = False

    # Build output - map sub-sections to Miro anchors
    result = {
        "title": title,
        "sections": {
            "customer_segments": sections.get("customer_segments", []),
            "early_adopters": sections.get("early_adopters", []),
            "problems": sections.get("problems", []),
            "existing_alternatives": sections.get("existing_alternatives", []),
            "uvp": sections.get("uvp_statement", []) or sections.get("uvp", []),
            "high_level_concept": sections.get("high_level_concept", []),
            "solutions": sections.get("solutions", []),
            "channels": sections.get("channels", []),
            "revenue": sections.get("revenue", []),
            "costs": sections.get("costs", []),
            "key_metrics": sections.get("nsm", []) + sections.get("kpi", []) + sections.get("key_metrics", []),
            "unfair_advantage": sections.get("unfair_advantage", []),
        },
        "anchor_map": ANCHOR_MAP,
    }

    # Stats
    total = sum(len(v) for v in result["sections"].values())
    result["stats"] = {k: len(v) for k, v in result["sections"].items()}
    result["stats"]["total"] = total

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python lean_canvas_parser.py INPUT_MD [OUTPUT_JSON]", file=sys.stderr)
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()

    result = parse_md(text)

    # Summary to stderr
    print(f"\n=== Lean Canvas Parse Result ===", file=sys.stderr)
    print(f"Title: {result['title']}", file=sys.stderr)
    print(f"Total: {result['stats']['total']} items\n", file=sys.stderr)

    for key, items in result["sections"].items():
        if items:
            print(f"  {key}: {len(items)}件", file=sys.stderr)

    # Output JSON
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(output)
        print(f"\nWritten to {sys.argv[2]}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
