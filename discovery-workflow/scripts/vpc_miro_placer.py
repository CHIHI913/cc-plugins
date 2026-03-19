#!/usr/bin/env python3
"""Place VPC sticky notes on a Miro board.

Usage: python miro_placer.py BOARD_ID FRAME_ID INPUT_JSON

INPUT_JSON format: see vpc-parser.md output format.
Script handles: anchor detection, position calculation, phase headers,
connectors, bulk content placement, and verification.
"""

import json, os, re, sys, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

# Layout constants
BATCH_SIZE = 20
API_DELAY = 0.1
STICKY_W, STICKY_H = 199, 228
PHASE_COL_PITCH = 279  # 199 + 80 (connector space)
GRID_GAP = 10
GRID_COLS = 3
ANCHOR_Y_OFFSET = 60

TYPE_TO_COLOR = {
    "verified": "light_green",
    "fact": "light_blue",
    "hypothesis": "light_yellow",
    "new": "light_pink",
    "rejected": "red",
}

ALL_LEGEND_ITEMS = [
    ("verified", "📗 検証済み", "light_green"),
    ("fact", "📘 事実", "light_blue"),
    ("hypothesis", "💡 仮説", "light_yellow"),
    ("rejected", "❌ 棄却", "red"),
    ("new", "⭐ 新発見", "light_pink"),
]
LEGEND_GAP = 20  # gap between legend sticky notes

# Static fallback positions (ratio of frame width W / height H)
STATIC_FALLBACK = {
    "jobs":          (0.75, 0.25),
    "pains":         (0.625, 0.65),
    "gains":         (0.72, 0.65),
    "products":      (0.25, 0.50),
    "painRelievers": (0.35, 0.50),
    "gainCreators":  (0.45, 0.50),
}

# Anchor patterns (order matters: longer/more specific first)
ANCHOR_PATTERNS = [
    ("Pain Relievers", "painRelievers"),
    ("Gain Creators", "gainCreators"),
    ("Products and Services", "products"),
    ("Customer Jobs", "jobs"),
    ("Pains", "pains"),
    ("Gains", "gains"),
    ("事実", "facts"),
    ("分析", "analysis"),
    ("凡例", "legend"),
]
NUMBERED_PATTERNS = [("戦略", "strategy"), ("提案", "proposal")]


def load_creds():
    creds = {}
    with open(os.path.expanduser("~/.zshrc.secrets")) as f:
        for line in f:
            m = re.match(r'^export (MIRO_\w+)=["\']?([^"\']*)["\']?', line.strip())
            if m:
                creds[m.group(1)] = m.group(2)
    return creds


class MiroAPI:
    def __init__(self, board_id, creds):
        self.board_id = board_id
        self.base = f"https://api.miro.com/v2/boards/{board_id}"
        self.token = creds.get("MIRO_ACCESS_TOKEN", "")
        self.creds = creds
        self._refreshed = False

    def _req(self, method, url, body=None):
        for attempt in range(4):
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            data = json.dumps(body).encode() if body else None
            req = Request(url, data=data, headers=headers, method=method)
            try:
                with urlopen(req) as resp:
                    if resp.status == 204:
                        return None
                    return json.loads(resp.read())
            except HTTPError as e:
                if e.code == 401 and not self._refreshed:
                    self._refresh_token()
                    continue
                elif e.code == 429:
                    wait = 2 ** attempt
                    print(f"  429 rate limit, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    err = e.read().decode()[:300] if e.fp else ""
                    print(f"  ERROR {e.code}: {err}", file=sys.stderr)
                    raise
            finally:
                time.sleep(API_DELAY)
        raise Exception(f"Max retries: {method} {url}")

    def _refresh_token(self):
        print("  Refreshing token...")
        data = urlencode({
            "grant_type": "refresh_token",
            "client_id": self.creds.get("MIRO_CLIENT_ID", ""),
            "client_secret": self.creds.get("MIRO_CLIENT_SECRET", ""),
            "refresh_token": self.creds.get("MIRO_REFRESH_TOKEN", ""),
        }).encode()
        req = Request(
            "https://api.miro.com/v1/oauth/token", data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST",
        )
        with urlopen(req) as resp:
            result = json.loads(resp.read())
        self.token = result["access_token"]
        self.creds["MIRO_REFRESH_TOKEN"] = result.get("refresh_token", "")
        self._refreshed = True
        print("  Token refreshed.")

    def get_frame(self, frame_id):
        return self._req("GET", f"{self.base}/items/{frame_id}")

    def get_frame_items(self, frame_id):
        items, cursor = [], None
        while True:
            url = f"{self.base}/items?parent_item_id={frame_id}&limit=50"
            if cursor:
                url += f"&cursor={cursor}"
            resp = self._req("GET", url)
            items.extend(resp.get("data", []))
            cursor = resp.get("cursor")
            if not cursor:
                break
        return items

    def create_sticky(self, frame_id, content, color, x, y):
        body = {
            "data": {"content": content, "shape": "square"},
            "style": {"fillColor": color},
            "position": {"x": x, "y": y},
            "parent": {"id": frame_id},
        }
        return self._req("POST", f"{self.base}/sticky_notes", body)["id"]

    def create_connector(self, start_id, end_id):
        body = {
            "startItem": {"id": str(start_id)},
            "endItem": {"id": str(end_id)},
            "style": {"strokeColor": "#808080", "strokeWidth": "2.0"},
        }
        return self._req("POST", f"{self.base}/connectors", body)

    def bulk_create(self, frame_id, items_data):
        total = 0
        for i in range(0, len(items_data), BATCH_SIZE):
            batch = items_data[i:i + BATCH_SIZE]
            payload = [{
                "type": "sticky_note",
                "data": {"content": it["content"]},
                "style": {"fillColor": it["color"]},
                "position": {"x": it["x"], "y": it["y"]},
                "parent": {"id": frame_id},
            } for it in batch]
            resp = self._req("POST", f"{self.base}/items/bulk", payload)
            created = len(resp.get("data", []))
            total += created
            print(f"  Batch {i // BATCH_SIZE + 1}: {created}/{len(batch)}")
        return total

    def count_stickies(self, frame_id):
        return sum(1 for i in self.get_frame_items(frame_id) if i.get("type") == "sticky_note")


def find_anchors(items):
    anchors = {}
    for item in items:
        if item.get("type") not in ("shape", "text"):
            continue
        text = item.get("data", {}).get("content") or item.get("data", {}).get("plainText") or ""
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '').strip()
        if not text:
            continue
        pos = item.get("position", {})
        geo = item.get("geometry", {})
        xy = {
            "x": pos.get("x", 0), "y": pos.get("y", 0),
            "w": geo.get("width", 0), "h": geo.get("height", 0),
        }

        # Fixed patterns (check longer first)
        matched = False
        for keyword, key in ANCHOR_PATTERNS:
            if keyword.lower() in text.lower():
                anchors[key] = xy
                matched = True
                break
        if matched:
            continue

        # Numbered/lettered patterns (戦略1, 戦略A, 提案2, 提案B, etc.)
        for keyword, prefix in NUMBERED_PATTERNS:
            m = re.search(rf'{keyword}\s*(\d+|[A-Za-z])', text)
            if m:
                anchors[f"{prefix}_{m.group(1).upper()}"] = xy
            elif keyword in text and prefix not in anchors:
                anchors[prefix] = xy
    return anchors


def get_color(item):
    return TYPE_TO_COLOR.get(item.get("type", "hypothesis"), "light_yellow")


def center_origin(ax, ay, area_w, area_h, layout_w, layout_h):
    """Calculate first sticky center (start_x, start_y) so layout is centered.

    ax: area shape center x (Miro positions are center-based).
    ay: area shape center y + ANCHOR_Y_OFFSET.
    area_w, area_h: full dimensions of the area shape.
    layout_w, layout_h: visual dimensions of the sticky group.

    Returns (start_x, start_y) — center of the top-left sticky.
    Falls back to (ax, ay) when area dimensions are unknown.
    """
    if area_w > 0 and area_h > 0:
        start_x = ax - layout_w / 2 + STICKY_W / 2

        area_cy = ay - ANCHOR_Y_OFFSET
        usable_top = area_cy - area_h / 2 + ANCHOR_Y_OFFSET
        usable_bottom = area_cy + area_h / 2
        usable_h = usable_bottom - usable_top

        if layout_h <= usable_h:
            usable_cy = (usable_top + usable_bottom) / 2
            start_y = usable_cy - layout_h / 2 + STICKY_H / 2
        else:
            start_y = usable_top + STICKY_H / 2
    else:
        start_x = ax
        start_y = ay
    return start_x, start_y


def build_phase_layout(section_items, ax, ay, area_w=0, area_h=0):
    """Returns (phase_headers, content_items), centered within area."""
    phase_order, phase_groups = [], {}
    for item in section_items:
        phase = item.get("phase", "")
        if phase not in phase_groups:
            phase_order.append(phase)
            phase_groups[phase] = []
        phase_groups[phase].append(item)

    n_phases = len(phase_order)
    if n_phases == 0:
        return [], []

    layout_w = (n_phases - 1) * PHASE_COL_PITCH + STICKY_W
    max_items = max(len(phase_groups[p]) for p in phase_order)
    layout_h = STICKY_H + 20 + max_items * STICKY_H + max(0, max_items - 1) * GRID_GAP

    start_x, start_y = center_origin(ax, ay, area_w, area_h, layout_w, layout_h)

    headers, contents = [], []
    for pi, phase in enumerate(phase_order):
        px = start_x + pi * PHASE_COL_PITCH
        headers.append({"content": phase, "color": "gray", "x": px, "y": start_y})
        for ri, item in enumerate(phase_groups[phase]):
            contents.append({
                "content": item["content"],
                "color": get_color(item),
                "x": px,
                "y": start_y + STICKY_H + 20 + ri * (STICKY_H + GRID_GAP),
            })
    return headers, contents


def build_grid_layout(section_items, ax, ay, area_w=0, area_h=0):
    """Place stickies in a centered grid."""
    import math
    n = len(section_items)
    if n == 0:
        return []
    actual_cols = min(n, GRID_COLS)
    n_rows = math.ceil(n / GRID_COLS)
    grid_w = actual_cols * STICKY_W + (actual_cols - 1) * GRID_GAP
    grid_h = n_rows * STICKY_H + (n_rows - 1) * GRID_GAP

    start_x, start_y = center_origin(ax, ay, area_w, area_h, grid_w, grid_h)

    return [{
        "content": item["content"],
        "color": get_color(item),
        "x": start_x + (i % GRID_COLS) * (STICKY_W + GRID_GAP),
        "y": start_y + (i // GRID_COLS) * (STICKY_H + GRID_GAP),
    } for i, item in enumerate(section_items)]


def main():
    if len(sys.argv) != 4:
        print("Usage: python miro_placer.py BOARD_ID FRAME_ID INPUT_JSON")
        sys.exit(1)

    board_id, frame_id, data_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(data_path) as f:
        data = json.load(f)

    creds = load_creds()
    api = MiroAPI(board_id, creds)

    # 1. Frame info
    print("1. Frame info...")
    frame = api.get_frame(frame_id)
    fw = frame.get("geometry", {}).get("width", 2400)
    fh = frame.get("geometry", {}).get("height", 1600)
    print(f"   {fw} x {fh}")

    # 2. Anchors
    print("2. Anchors...")
    items = api.get_frame_items(frame_id)
    pre_stickies = sum(1 for i in items if i.get("type") == "sticky_note")
    anchors = find_anchors(items)
    print(f"   Found: {', '.join(sorted(anchors.keys()))}")
    print(f"   Pre-existing stickies: {pre_stickies}")

    # 3. Calculate positions
    print("3. Positions...")
    phase_sections = []  # [{section, headers}]
    all_content = []

    # Customer Profile (phase-based)
    cp = data.get("customerProfile", {})
    for key in ["jobs", "pains", "gains"]:
        items_list = cp.get(key, [])
        if not items_list:
            continue
        if key in anchors:
            a = anchors[key]
        elif key in STATIC_FALLBACK:
            rx, ry = STATIC_FALLBACK[key]
            a = {"x": fw * rx, "y": fh * ry}
            print(f"   {key}: using static fallback ({a['x']:.0f}, {a['y']:.0f})")
        else:
            print(f"   WARN: no anchor for {key}")
            continue
        headers, contents = build_phase_layout(items_list, a["x"], a["y"] + ANCHOR_Y_OFFSET, a.get("w", 0), a.get("h", 0))
        phase_sections.append({"section": key, "headers": headers})
        all_content.extend(contents)
        print(f"   {key}: {len(headers)} phases, {len(contents)} items")

    # Value Map (grid)
    vm = data.get("valueMap", {})
    for key in ["painRelievers", "gainCreators", "products"]:
        items_list = vm.get(key, [])
        if not items_list:
            continue
        if key in anchors:
            a = anchors[key]
        elif key in STATIC_FALLBACK:
            rx, ry = STATIC_FALLBACK[key]
            a = {"x": fw * rx, "y": fh * ry}
            print(f"   {key}: using static fallback ({a['x']:.0f}, {a['y']:.0f})")
        else:
            print(f"   WARN: no anchor for {key}")
            continue
        grid = build_grid_layout(items_list, a["x"], a["y"] + ANCHOR_Y_OFFSET, a.get("w", 0), a.get("h", 0))
        all_content.extend(grid)
        print(f"   {key}: {len(grid)} items (grid)")

    # Deep Dive (grid)
    dd = data.get("deepDive", {})
    for key in ["facts", "analysis"]:
        items_list = dd.get(key, [])
        if not items_list or key not in anchors:
            if items_list:
                print(f"   WARN: no anchor for {key}")
            continue
        a = anchors[key]
        grid = build_grid_layout(items_list, a["x"], a["y"] + ANCHOR_Y_OFFSET, a.get("w", 0), a.get("h", 0))
        all_content.extend(grid)
        print(f"   {key}: {len(grid)} items (grid)")

    # Strategies (numbered)
    for num, items_list in dd.get("strategies", {}).items():
        if not items_list:
            continue
        akey = f"strategy_{num}"
        a = anchors.get(akey) or anchors.get("strategy")
        if not a:
            print(f"   WARN: no anchor for 戦略{num}")
            continue
        grid = build_grid_layout(items_list, a["x"], a["y"] + ANCHOR_Y_OFFSET, a.get("w", 0), a.get("h", 0))
        all_content.extend(grid)
        print(f"   戦略{num}: {len(grid)} items (grid)")

    # Proposals (numbered)
    for num, items_list in dd.get("proposals", {}).items():
        if not items_list:
            continue
        akey = f"proposal_{num}"
        a = anchors.get(akey) or anchors.get("proposal")
        if not a:
            print(f"   WARN: no anchor for 提案{num}")
            continue
        grid = build_grid_layout(items_list, a["x"], a["y"] + ANCHOR_Y_OFFSET, a.get("w", 0), a.get("h", 0))
        all_content.extend(grid)
        print(f"   提案{num}: {len(grid)} items (grid)")

    n_headers = sum(len(s["headers"]) for s in phase_sections)
    n_connectors = sum(max(0, len(s["headers"]) - 1) for s in phase_sections)
    n_content = len(all_content)
    # Build legend from types actually present in source data + always include rejected
    used_types = set()
    cp = data["customerProfile"]
    vm = data["valueMap"]
    dd = data["deepDive"]
    for items_list in [cp["jobs"], cp["pains"], cp["gains"],
                       vm["painRelievers"], vm["gainCreators"], vm["products"],
                       dd["facts"], dd["analysis"]]:
        for item in items_list:
            used_types.add(item.get("type", "hypothesis"))
    for group in [dd["strategies"], dd["proposals"]]:
        for items_list in group.values():
            for item in items_list:
                used_types.add(item.get("type", "hypothesis"))
    # Always include "rejected" (❌ rows are skipped from data but shown in legend)
    ALWAYS_SHOW = {"rejected"}
    legend_filtered = [(label, color) for typ, label, color in ALL_LEGEND_ITEMS if typ in used_types or typ in ALWAYS_SHOW]

    n_legend = len(legend_filtered)
    print(f"\n   Summary: {n_legend} legend + {n_headers} headers + {n_connectors} connectors + {n_content} content = {n_legend + n_headers + n_content} stickies")

    # 4. Legend (placed relative to "凡例" anchor, or fallback to top-left)
    print("\n4. Legend...")
    legend_items = []
    if "legend" in anchors:
        la = anchors["legend"]
        row_w = n_legend * STICKY_W + (n_legend - 1) * LEGEND_GAP
        lx, ly = center_origin(
            la["x"], la["y"] + ANCHOR_Y_OFFSET,
            la.get("w", 0), la.get("h", 0), row_w, STICKY_H,
        )
        print(f"   Anchor: ({la['x']}, {la['y']}), area: {la.get('w',0)}x{la.get('h',0)}")
    else:
        lx, ly = 50, 50
        print("   WARN: no anchor for 凡例, using (50, 50)")
    for i, (label, color) in enumerate(legend_filtered):
        legend_items.append({
            "content": label,
            "color": color,
            "x": lx + i * (STICKY_W + LEGEND_GAP),
            "y": ly,
        })
    api.bulk_create(frame_id, legend_items)
    print(f"   {n_legend} items (types: {sorted(used_types)})")

    # 5. Create phase headers + connectors
    print("\n5. Phase headers & connectors...")
    for sec in phase_sections:
        header_ids = []
        for h in sec["headers"]:
            hid = api.create_sticky(frame_id, h["content"], h["color"], h["x"], h["y"])
            header_ids.append(hid)
        for i in range(len(header_ids) - 1):
            api.create_connector(header_ids[i], header_ids[i + 1])
        print(f"   {sec['section']}: {len(header_ids)} headers, {len(header_ids) - 1} connectors")

    # 6. Bulk create content
    print(f"\n6. Content ({n_content} items)...")
    created = api.bulk_create(frame_id, all_content)

    # 7. Verify
    print("\n7. Verify...")
    expected_new = n_legend + n_headers + n_content
    actual = api.count_stickies(frame_id)
    actual_new = actual - pre_stickies
    print(f"   New: {actual_new} (expected {expected_new})")
    if actual_new == expected_new:
        print("   OK")
    else:
        print(f"   MISMATCH: {actual_new - expected_new:+d}")

    print(f"\nDone: {expected_new} stickies + {n_connectors} connectors")


if __name__ == "__main__":
    main()
