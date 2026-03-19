#!/usr/bin/env python3
"""Parse standardized VPC Markdown into JSON for miro_placer.py.

Usage: python vpc_parser.py INPUT_MD [OUTPUT_JSON]

If OUTPUT_JSON is omitted, prints to stdout.
Rules: see vpc-parser.md
"""

import json, re, sys

# Label → type mapping
LABEL_MAP = {
    "📗": "verified",
    "📘": "fact",
    "💡": "hypothesis",
    "⭐": "new",
    "❌": "rejected",
}

# Section detection: (keyword, section_key, exclude_keyword)
SECTION_PATTERNS = [
    ("Pain Relievers", "painRelievers", None),
    ("Gain Creators", "gainCreators", None),
    ("Products & Services", "products", None),
    ("Products and Services", "products", None),
    ("Customer Jobs", "jobs", None),
    ("Pains", "pains", "Pain Relievers"),
    ("Gains", "gains", "Gain Creators"),
]
DEEP_DIVE_PATTERNS = [
    ("事実", "facts", None),
    ("分析", "analysis", None),
]
NUMBERED_PATTERNS = [("戦略", "strategy"), ("提案", "proposal")]

# Section categories
CP_SECTIONS = {"jobs", "pains", "gains"}
VM_SECTIONS = {"painRelievers", "gainCreators", "products"}
DD_SECTIONS = {"facts", "analysis"}


def detect_section(header_text):
    """Detect section key from ### header text."""
    clean = header_text.strip().lstrip("#").strip()
    # Remove numbering like "1. "
    clean_no_num = re.sub(r'^\d+\.\s*', '', clean)

    # Numbered/lettered patterns (戦略1, 戦略A, 提案2, 提案B, etc.)
    for keyword, prefix in NUMBERED_PATTERNS:
        m = re.search(rf'{keyword}\s*(\d+|[A-Za-z])', clean_no_num)
        if m:
            return f"{prefix}_{m.group(1).upper()}"
        if keyword in clean_no_num:
            return prefix

    # Fixed patterns (longer/more specific first)
    for keyword, key, exclude in SECTION_PATTERNS:
        if exclude and exclude.lower() in clean_no_num.lower():
            continue
        if keyword.lower() in clean_no_num.lower():
            return key

    # Deep dive patterns
    for keyword, key, _ in DEEP_DIVE_PATTERNS:
        if keyword in clean_no_num:
            return key

    return None


def parse_label(cell):
    """Extract type from label emoji."""
    cell = cell.strip()
    for emoji, typ in LABEL_MAP.items():
        if emoji in cell:
            return typ, emoji
    return "hypothesis", ""


def is_rejected(row_text):
    """Check if row should be skipped (❌ or ~~text~~)."""
    if "❌" in row_text:
        return True
    if re.search(r'~~[^~]+~~', row_text):
        return True
    return False


def is_separator(row_text):
    """Check if row is a table separator (|---|---|)."""
    return bool(re.match(r'^\s*\|[\s\-:]+\|', row_text))


def is_table_header_label(row_text):
    """Check if row is a table header with 'ラベル' as first column."""
    cells = [c.strip() for c in row_text.strip().strip("|").split("|")]
    return len(cells) >= 2 and cells[0].strip() == "ラベル"


def parse_table_row(row_text):
    """Parse a table row into cells."""
    return [c.strip() for c in row_text.strip().strip("|").split("|")]


def parse_md(text):
    """Parse VPC Markdown into structured data."""
    lines = text.split("\n")
    title = ""
    sections = {}  # key -> list of items
    current_section = None
    in_table = False
    skipped = 0

    for line in lines:
        stripped = line.strip()

        # Extract title from # heading
        if stripped.startswith("# ") and not title:
            title = "VPC: " + stripped.lstrip("#").strip()
            continue

        # Detect ### section headers
        if stripped.startswith("### "):
            sec = detect_section(stripped)
            if sec:
                current_section = sec
                if sec not in sections:
                    sections[sec] = []
            else:
                current_section = None
            in_table = False
            continue

        # Skip if no active section
        if current_section is None:
            continue

        # Table processing
        if stripped.startswith("|"):
            # Separator row
            if is_separator(stripped):
                continue

            # Header row check
            if is_table_header_label(stripped):
                in_table = True
                continue
            elif not in_table:
                # Non-ラベル table header or content without prior ラベル header → skip
                cells = parse_table_row(stripped)
                if len(cells) >= 2 and not any(c.strip() == "" for c in cells[:1]):
                    # Looks like a table header for a non-target table
                    in_table = False
                continue

            # Data row in active table
            if in_table:
                cells = parse_table_row(stripped)
                if len(cells) < 2:
                    continue

                typ, label = parse_label(cells[0])
                item = {"type": typ, "label": label}

                if current_section in CP_SECTIONS:
                    # col1=ラベル, col2=フェーズ, col3=content
                    item["phase"] = cells[1] if len(cells) > 1 else ""
                    item["content"] = cells[2] if len(cells) > 2 else ""
                elif current_section in VM_SECTIONS:
                    # col1=ラベル, col2=ref, col3=content
                    item["ref"] = cells[1] if len(cells) > 1 else ""
                    item["content"] = cells[2] if len(cells) > 2 else ""
                elif current_section in DD_SECTIONS:
                    # col1=ラベル, col2=content
                    item["content"] = cells[1] if len(cells) > 1 else ""
                else:
                    # Numbered strategy/proposal: col1=ラベル, col2=content
                    item["content"] = cells[1] if len(cells) > 1 else ""

                # Skip empty content
                if not item.get("content", "").strip():
                    continue

                sections[current_section].append(item)
        else:
            # Non-table line → end table mode
            if in_table and stripped:
                in_table = False

    # Build output structure
    result = {
        "title": title,
        "customerProfile": {
            "jobs": sections.get("jobs", []),
            "pains": sections.get("pains", []),
            "gains": sections.get("gains", []),
        },
        "valueMap": {
            "painRelievers": sections.get("painRelievers", []),
            "gainCreators": sections.get("gainCreators", []),
            "products": sections.get("products", []),
        },
        "deepDive": {
            "facts": sections.get("facts", []),
            "analysis": sections.get("analysis", []),
            "strategies": {},
            "proposals": {},
        },
    }

    # Collect numbered strategies/proposals
    for key, items in sections.items():
        m = re.match(r'(strategy|proposal)_(\d+|[A-Za-z])', key)
        if m:
            prefix, num = m.group(1), m.group(2)
            if prefix == "strategy":
                result["deepDive"]["strategies"][num] = items
            else:
                result["deepDive"]["proposals"][num] = items
        elif key == "strategy" and items:
            result["deepDive"]["strategies"]["1"] = items
        elif key == "proposal" and items:
            result["deepDive"]["proposals"]["1"] = items

    # Stats
    cp = result["customerProfile"]
    vm = result["valueMap"]
    dd = result["deepDive"]
    strat_count = sum(len(v) for v in dd["strategies"].values())
    prop_count = sum(len(v) for v in dd["proposals"].values())
    total = (
        len(cp["jobs"]) + len(cp["pains"]) + len(cp["gains"])
        + len(vm["painRelievers"]) + len(vm["gainCreators"]) + len(vm["products"])
        + len(dd["facts"]) + len(dd["analysis"])
        + strat_count + prop_count
    )
    result["stats"] = {
        "jobs": len(cp["jobs"]),
        "pains": len(cp["pains"]),
        "gains": len(cp["gains"]),
        "painRelievers": len(vm["painRelievers"]),
        "gainCreators": len(vm["gainCreators"]),
        "products": len(vm["products"]),
        "facts": len(dd["facts"]),
        "analysis": len(dd["analysis"]),
        "strategy": strat_count,
        "proposal": prop_count,
        "skipped": skipped,
        "total": total,
    }

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python vpc_parser.py INPUT_MD [OUTPUT_JSON]", file=sys.stderr)
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, encoding="utf-8") as f:
        text = f.read()

    result = parse_md(text)

    # Print detailed summary to stderr (used for user confirmation)
    s = result["stats"]
    cp = result["customerProfile"]
    vm = result["valueMap"]
    dd = result["deepDive"]

    print(f"\n=== VPC Parse Result ===", file=sys.stderr)
    print(f"Title: {result['title']}", file=sys.stderr)
    print(f"Total: {s['total']} items (skipped {s['skipped']})\n", file=sys.stderr)

    print(f"Customer Profile:", file=sys.stderr)
    for key, label in [("jobs", "Jobs"), ("pains", "Pains"), ("gains", "Gains")]:
        items = cp[key]
        phases = sorted(set(i.get("phase", "") for i in items if i.get("phase")))
        print(f"  {label}: {len(items)}件 phases={phases}", file=sys.stderr)

    print(f"\nValue Map:", file=sys.stderr)
    for key, label in [("painRelievers", "Pain Relievers"), ("gainCreators", "Gain Creators"), ("products", "Products & Services")]:
        print(f"  {label}: {len(vm[key])}件", file=sys.stderr)

    print(f"\nDeep Dive:", file=sys.stderr)
    print(f"  Facts: {len(dd['facts'])}件", file=sys.stderr)
    print(f"  Analysis: {len(dd['analysis'])}件", file=sys.stderr)
    for prefix, name in [("strategies", "Strategy"), ("proposals", "Proposal")]:
        for num, items_list in sorted(dd[prefix].items()):
            print(f"  {name} {num}: {len(items_list)}件", file=sys.stderr)

    # Type distribution
    type_counts = {}
    all_items = (
        cp["jobs"] + cp["pains"] + cp["gains"]
        + vm["painRelievers"] + vm["gainCreators"] + vm["products"]
        + dd["facts"] + dd["analysis"]
        + [i for v in dd["strategies"].values() for i in v]
        + [i for v in dd["proposals"].values() for i in v]
    )
    for item in all_items:
        t = item.get("type", "unknown")
        type_counts[t] = type_counts.get(t, 0) + 1
    print(f"\nType distribution:", file=sys.stderr)
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}", file=sys.stderr)

    # Output JSON
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if len(sys.argv) >= 3:
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Written to {sys.argv[2]}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
