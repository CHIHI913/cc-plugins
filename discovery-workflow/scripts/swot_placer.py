#!/usr/bin/env python3
"""Place PEST items on Miro board.

Usage: python pest_placer.py BOARD_ID FRAME_ID INPUT_JSON

All stickies are light_yellow.
"""

import json, math, os, re, sys, time
from urllib.request import Request, urlopen
from urllib.error import HTTPError

STICKY_W = 199
STICKY_H = 228
GAP = 10

ANCHOR_PATTERNS = [
    ("積極戦略", "so_strategy"),
    ("改善戦略", "wo_strategy"),
    ("差別化戦略", "st_strategy"),
    ("防衛戦略", "wt_strategy"),
    ("強み", "strengths"),
    ("弱み", "weaknesses"),
    ("機会", "opportunities"),
    ("脅威", "threats"),
    ("Strengths", "strengths"),
    ("Weaknesses", "weaknesses"),
    ("Opportunities", "opportunities"),
    ("Threats", "threats"),
]


class MiroAPI:
    def __init__(self, board_id):
        self.board_id = board_id
        self.base = f"https://api.miro.com/v2/boards/{board_id}"
        self.token = os.environ.get("MIRO_ACCESS_TOKEN", "")
        self.refreshed = False

    def _req(self, method, url, data=None, retry=0):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        body = json.dumps(data).encode() if data else None
        req = Request(url, data=body, headers=headers, method=method)
        try:
            with urlopen(req) as resp:
                return json.loads(resp.read())
        except HTTPError as e:
            if e.code == 401 and not self.refreshed:
                self._refresh_token()
                return self._req(method, url, data, retry)
            if e.code == 429 and retry < 3:
                time.sleep(2 ** retry)
                return self._req(method, url, data, retry + 1)
            body = e.read().decode()
            print(f"  ERROR {e.code}: {body[:200]}", file=sys.stderr)
            raise

    def _refresh_token(self):
        cid = os.environ.get("MIRO_CLIENT_ID", "")
        csecret = os.environ.get("MIRO_CLIENT_SECRET", "")
        rtoken = os.environ.get("MIRO_REFRESH_TOKEN", "")
        from urllib.parse import urlencode
        data = urlencode({"grant_type": "refresh_token", "client_id": cid, "client_secret": csecret, "refresh_token": rtoken})
        req = Request(
            "https://api.miro.com/v1/oauth/token",
            data=data.encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urlopen(req) as resp:
            r = json.loads(resp.read())
        self.token = r["access_token"]
        os.environ["MIRO_ACCESS_TOKEN"] = self.token
        self.refreshed = True

    def get_frame(self, frame_id):
        return self._req("GET", f"{self.base}/items/{frame_id}")

    def get_items(self, frame_id):
        items = []
        cursor = ""
        while True:
            url = f"{self.base}/items?parent_item_id={frame_id}&limit=50"
            if cursor:
                url += f"&cursor={cursor}"
            r = self._req("GET", url)
            items.extend(r.get("data", []))
            cursor = r.get("cursor", "")
            if not cursor:
                break
        return items

    def bulk_create(self, frame_id, items):
        total = 0
        for i in range(0, len(items), 20):
            batch = items[i:i + 20]
            payload = []
            for item in batch:
                payload.append({
                    "type": "sticky_note",
                    "data": {"content": item["content"]},
                    "style": {"fillColor": item.get("color", "light_yellow")},
                    "geometry": {"width": item.get("width", STICKY_W)},
                    "position": {"x": item["x"], "y": item["y"]},
                    "parent": {"id": str(frame_id)},
                })
            r = self._req("POST", f"{self.base}/items/bulk", payload)
            created = len(r.get("data", []))
            total += created
            print(f"  Batch {i // 20 + 1}: {created}/{len(batch)}")
            time.sleep(0.1)
        return total


def detect_anchors(items):
    anchors = {}
    for item in items:
        if item["type"] not in ("shape", "text"):
            continue
        text = item.get("data", {}).get("content", "") or ""
        text = re.sub(r'<[^>]+>', '', text)
        text = text.replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '').strip()
        if not text:
            continue
        x = item["position"]["x"]
        y = item["position"]["y"]
        w = item.get("geometry", {}).get("width", 0) or 0
        h = item.get("geometry", {}).get("height", 0) or 0

        for keyword, key in ANCHOR_PATTERNS:
            if keyword in text:
                anchors[key] = {"x": x, "y": y, "w": w, "h": h}
                break
    return anchors


def center_origin(ax, ay, area_w, area_h, layout_w, layout_h):
    start_x = ax - area_w / 2 + (area_w - layout_w) / 2 + STICKY_W / 2
    start_y = ay - area_h / 2 + (area_h - layout_h) / 2 + STICKY_H / 2
    return start_x, start_y


def grid_items(items, anchor, cols=2):
    if not anchor or not items:
        return []
    n = len(items)
    layout_w = cols * STICKY_W + (cols - 1) * GAP
    layout_h = math.ceil(n / cols) * STICKY_H + (math.ceil(n / cols) - 1) * GAP
    sx, sy = center_origin(
        anchor["x"], anchor["y"],
        anchor.get("w", 0), anchor.get("h", 0),
        layout_w, layout_h,
    )
    result = []
    for i, item in enumerate(items):
        col = i % cols
        row = i // cols
        # items can be dicts with content/highlight or plain strings
        if isinstance(item, dict):
            content = item["content"]
            color = "light_pink" if item.get("highlight") else "light_yellow"
        else:
            content = item
            color = "light_yellow"
        result.append({
            "content": content,
            "color": color,
            "x": sx + col * (STICKY_W + GAP),
            "y": sy + row * (STICKY_H + GAP),
        })
    return result


def main():
    if len(sys.argv) < 4:
        print("Usage: python pest_placer.py BOARD_ID FRAME_ID INPUT_JSON", file=sys.stderr)
        sys.exit(1)

    board_id = sys.argv[1]
    frame_id = sys.argv[2]
    input_path = sys.argv[3]

    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)

    api = MiroAPI(board_id)

    print("1. Frame info...")
    frame = api.get_frame(frame_id)
    fw = frame.get("geometry", {}).get("width", 0)
    fh = frame.get("geometry", {}).get("height", 0)
    print(f"   {fw} x {fh}")

    print("2. Anchors...")
    items = api.get_items(frame_id)
    anchors = detect_anchors(items)
    pre_stickies = sum(1 for i in items if i["type"] == "sticky_note")
    print(f"   Found: {', '.join(sorted(anchors.keys()))}")
    print(f"   Pre-existing stickies: {pre_stickies}")

    print("3. Positions...")
    sections = data["sections"]
    all_stickies = []

    for key, items_list in sections.items():
        if not items_list:
            continue
        anchor = anchors.get(key)
        if not anchor:
            print(f"   WARN: no anchor for {key}, skipping {len(items_list)} items")
            continue

        area_w = anchor.get("w", 0)
        if area_w > 2000:
            cols = 3
        elif area_w > 1200:
            cols = 2
        else:
            cols = 1

        grid = grid_items(items_list, anchor, cols)
        all_stickies.extend(grid)
        print(f"   {key}: {len(grid)} items ({cols} cols)")

    n_total = len(all_stickies)
    print(f"\n   Total: {n_total} stickies")

    print(f"\n4. Creating {n_total} stickies...")
    api.bulk_create(frame_id, all_stickies)

    print("\n5. Verify...")
    all_items = api.get_items(frame_id)
    new_stickies = sum(1 for i in all_items if i["type"] == "sticky_note") - pre_stickies
    print(f"   New: {new_stickies} (expected {n_total})")
    if new_stickies == n_total:
        print("   OK")
    else:
        print("   MISMATCH!")

    print(f"\nDone: {new_stickies} stickies")


if __name__ == "__main__":
    main()
