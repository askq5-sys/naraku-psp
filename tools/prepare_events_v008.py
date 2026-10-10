#!/usr/bin/env python3
import argparse
import json
import re
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCREEN_W = 480
DIALOG_TEX_W = 512
DIALOG_TEX_H = 128
DIALOG_VISIBLE_H = 96
LANG_TAGS = ["en", "ja", "zhcn", "zhtw"]
LANG_KEYS = ["en_US", "ja_JP", "zh_CN", "zh_TW"]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rgba8888_bytes(img: Image.Image) -> bytes:
    return img.convert("RGBA").tobytes()


def find_font() -> Path:
    candidates = [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise RuntimeError("Install a CJK font: sudo apt install -y fonts-noto-cjk")


def font_index_for_lang(lang: int) -> int:
    return {0: 0, 1: 0, 2: 2, 3: 3}.get(lang, 0)


def get_font(path: Path, size: int, idx: int):
    try:
        return ImageFont.truetype(str(path), size, index=idx)
    except TypeError:
        return ImageFont.truetype(str(path), size)


def wrap_pixels(draw, text, font, max_width):
    if not text:
        return [""]
    lines = []
    cur = ""
    # Works for both space-delimited Latin and CJK. Preserve words when practical.
    tokens = re.findall(r"\S+\s*", text) if " " in text else list(text)
    for tok in tokens:
        candidate = cur + tok
        bbox = draw.textbbox((0, 0), candidate.rstrip(), font=font)
        width = bbox[2] - bbox[0]
        if cur and width > max_width:
            lines.append(cur.rstrip())
            cur = tok.lstrip() if " " in text else tok
        else:
            cur = candidate
    if cur:
        lines.append(cur.rstrip())
    return lines or [""]


def make_message_texture(lines, font_path: Path, font_idx: int):
    tex = Image.new("RGBA", (DIALOG_TEX_W, DIALOG_TEX_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)
    draw.rounded_rectangle(
        (6, 4, SCREEN_W - 6, DIALOG_VISIBLE_H - 4),
        radius=8,
        fill=(10, 10, 14, 224),
        outline=(210, 210, 220, 235),
        width=2,
    )
    font = get_font(font_path, 20, font_idx)
    rendered = []
    for source_line in lines:
        rendered.extend(wrap_pixels(draw, source_line, font, SCREEN_W - 48))
    rendered = rendered[:3]
    y = 15
    for line in rendered:
        draw.text((22, y), line, font=font, fill=(255, 255, 255, 255))
        y += 25
    draw.polygon([(449, 72), (463, 72), (456, 82)], fill=(255, 255, 255, 230))
    return tex


def i18n_ids_from_page(page):
    ids = []
    for cmd in page.get("list", []):
        if cmd.get("code") == 401:
            text = str(cmd.get("parameters", [""])[0])
            ids.extend(int(x) for x in re.findall(r"\\I18N\[(\d+)\]", text))
    return ids


def simple_action_page(page):
    codes = [c.get("code", 0) for c in page.get("list", []) if c.get("code", 0) != 0]
    return bool(codes) and all(code in (101, 401) for code in codes)


def page_available_after_intro(page):
    c = page.get("conditions", {})
    # 0.0.8 implements the post-intro Map001 state: switch 3 is ON.
    # Accept unconditional pages and the sign page gated only by switch 3.
    if c.get("switch2Valid") or c.get("variableValid") or c.get("selfSwitchValid") or c.get("itemValid") or c.get("actorValid"):
        return False
    if c.get("switch1Valid") and c.get("switch1Id") != 3:
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU PSP 0.0.8 Map001 interaction data")
    ap.add_argument("game", type=Path, help="Path to installed NARAKU")
    ap.add_argument("--out", type=Path, default=Path("assets"))
    args = ap.parse_args()

    game = args.game.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    map_data = read_json(game / "data" / "Map001.json")
    texts = read_json(game / "data" / "I18NTexts.json")
    w, h = map_data["width"], map_data["height"]
    if w != 17 or h != 15:
        raise RuntimeError(f"Unexpected Map001 size: {w}x{h}")

    action_map = bytearray(w * h)
    step_map = bytearray(w * h)
    simple_events = []

    for ev in map_data.get("events", []):
        if not ev:
            continue
        ex, ey = ev["x"], ev["y"]
        if not (0 <= ex < w and 0 <= ey < h):
            continue

        # Highest-numbered valid page wins in RPG Maker.
        chosen = None
        for page in ev.get("pages", []):
            if page_available_after_intro(page):
                chosen = page
        if chosen is None:
            continue

        if chosen.get("trigger") == 0 and simple_action_page(chosen):
            ids = i18n_ids_from_page(chosen)
            if ids:
                if ev["id"] > 255:
                    raise RuntimeError("Event id does not fit u8")
                action_map[ey * w + ex] = ev["id"]
                simple_events.append((ev["id"], ids, ev.get("name", ""), ex, ey))

        if chosen.get("trigger") == 1:
            for cmd in chosen.get("list", []):
                if cmd.get("code") == 250:
                    se = cmd.get("parameters", [{}])[0]
                    if "水をバシャッとかける1" in se.get("name", ""):
                        step_map[ey * w + ex] |= 0x01

    header = struct.pack("<4sHH", b"NPE8", w, h)
    (out / "map001_events.bin").write_bytes(header + action_map + step_map)

    font_path = find_font()
    for event_id, ids, name, ex, ey in simple_events:
        for lang, (tag, key) in enumerate(zip(LANG_TAGS, LANG_KEYS)):
            lines = [str(texts[i].get(key, "")) for i in ids]
            tex = make_message_texture(lines, font_path, font_index_for_lang(lang))
            raw = out / f"evt{event_id:03d}_{tag}.rgba8888"
            raw.write_bytes(rgba8888_bytes(tex))
        print(f"event {event_id:03d} @({ex},{ey}) {name}: I18N {ids}")

    print("\nNARAKU PSP 0.0.8 interaction data ready")
    print(f"  simple action events: {len(simple_events)}")
    print(f"  splash step tiles: {sum(1 for b in step_map if b & 1)}")
    print(f"  map001_events.bin: {(out / 'map001_events.bin').stat().st_size} bytes")
    print("  languages: English / Japanese / Simplified Chinese / Traditional Chinese")


if __name__ == "__main__":
    main()
