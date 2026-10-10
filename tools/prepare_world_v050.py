#!/usr/bin/env python3
import argparse
import io
import json
import math
import re
import struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TILE = 48
PSP_TILE = 24
ATLAS_W = 512
ATLAS_H = 512
ATLAS_SLOT = 50
ATLAS_COLS = 10
CHAR_TEX_W = 256
CHAR_TEX_H = 512
CHAR_SLOT_W = 50
CHAR_SLOT_H = 80
EVENT_ATLAS_W = 512
EVENT_ATLAS_H = 512
DIALOG_TEX_W = 512
DIALOG_TEX_H = 128
DIALOG_VISIBLE_H = 96
SCREEN_W = 480
MAP_IDS = range(1, 140)
LANG_TAGS = ["en", "ja", "zhcn", "zhtw"]
LANG_KEYS = ["en_US", "ja_JP", "zh_CN", "zh_TW"]
PICTURE_IDS = {}

FLOOR_AUTOTILE_TABLE = [
    [[2,4],[1,4],[2,3],[1,3]], [[2,0],[1,4],[2,3],[1,3]],
    [[2,4],[3,0],[2,3],[1,3]], [[2,0],[3,0],[2,3],[1,3]],
    [[2,4],[1,4],[2,3],[3,1]], [[2,0],[1,4],[2,3],[3,1]],
    [[2,4],[3,0],[2,3],[3,1]], [[2,0],[3,0],[2,3],[3,1]],
    [[2,4],[1,4],[2,1],[1,3]], [[2,0],[1,4],[2,1],[1,3]],
    [[2,4],[3,0],[2,1],[1,3]], [[2,0],[3,0],[2,1],[1,3]],
    [[2,4],[1,4],[2,1],[3,1]], [[2,0],[1,4],[2,1],[3,1]],
    [[2,4],[3,0],[2,1],[3,1]], [[2,0],[3,0],[2,1],[3,1]],
    [[0,4],[1,4],[0,3],[1,3]], [[0,4],[3,0],[0,3],[1,3]],
    [[0,4],[1,4],[0,3],[3,1]], [[0,4],[3,0],[0,3],[3,1]],
    [[2,2],[1,2],[2,3],[1,3]], [[2,2],[1,2],[2,3],[3,1]],
    [[2,2],[1,2],[2,1],[1,3]], [[2,2],[1,2],[2,1],[3,1]],
    [[2,4],[3,4],[2,3],[3,3]], [[2,4],[3,4],[2,1],[3,3]],
    [[2,0],[3,4],[2,3],[3,3]], [[2,0],[3,4],[2,1],[3,3]],
    [[2,4],[1,4],[2,5],[1,5]], [[2,0],[1,4],[2,5],[1,5]],
    [[2,4],[3,0],[2,5],[1,5]], [[2,0],[3,0],[2,5],[1,5]],
    [[0,4],[3,4],[0,3],[3,3]], [[2,2],[1,2],[2,5],[1,5]],
    [[0,2],[1,2],[0,3],[1,3]], [[0,2],[1,2],[0,3],[3,1]],
    [[2,2],[3,2],[2,3],[3,3]], [[2,2],[3,2],[2,1],[3,3]],
    [[2,4],[3,4],[2,5],[3,5]], [[2,0],[3,4],[2,5],[3,5]],
    [[0,4],[1,4],[0,5],[1,5]], [[0,4],[3,0],[0,5],[1,5]],
    [[0,2],[3,2],[0,3],[3,3]], [[0,2],[1,2],[0,5],[1,5]],
    [[0,4],[3,4],[0,5],[3,5]], [[2,2],[3,2],[2,5],[3,5]],
    [[0,2],[3,2],[0,5],[3,5]], [[0,0],[1,0],[0,1],[1,1]],
]

WALL_AUTOTILE_TABLE = [
    [[2,2],[1,2],[2,1],[1,1]], [[0,2],[1,2],[0,1],[1,1]],
    [[2,0],[1,0],[2,1],[1,1]], [[0,0],[1,0],[0,1],[1,1]],
    [[2,2],[3,2],[2,1],[3,1]], [[0,2],[3,2],[0,1],[3,1]],
    [[2,0],[3,0],[2,1],[3,1]], [[0,0],[3,0],[0,1],[3,1]],
    [[2,2],[1,2],[2,3],[1,3]], [[0,2],[1,2],[0,3],[1,3]],
    [[2,0],[1,0],[2,3],[1,3]], [[0,0],[1,0],[0,3],[1,3]],
    [[2,2],[3,2],[2,3],[3,3]], [[0,2],[3,2],[0,3],[3,3]],
    [[2,0],[3,0],[2,3],[3,3]], [[0,0],[3,0],[0,3],[3,3]],
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def decrypt_mz(src: Path, key: bytes) -> bytes:
    data = src.read_bytes()
    if len(data) < 32 or data[:8] != b"RPGMV\x00\x00\x00":
        raise RuntimeError(f"Not an encrypted RPG Maker resource: {src}")
    out = bytearray(data[16:])
    for i in range(min(16, len(out))):
        out[i] ^= key[i]
    return bytes(out)


def load_encrypted_png(src: Path, key: bytes) -> Image.Image:
    raw = decrypt_mz(src, key)
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Decryption did not produce PNG: {src}")
    return Image.open(io.BytesIO(raw)).convert("RGBA")


def alpha_paste(dst: Image.Image, src: Image.Image, x: int, y: int):
    dst.alpha_composite(src, (x, y))


def draw_normal_tile(dst, tile_id, dx, dy, bitmaps):
    if 1536 <= tile_id < 2048:
        set_number = 4
    else:
        set_number = 5 + tile_id // 256
    src = bitmaps.get(set_number)
    if src is None:
        raise RuntimeError(f"Missing tileset bitmap #{set_number} for tile {tile_id}")
    sx = (((tile_id // 128) % 2) * 8 + (tile_id % 8)) * TILE
    sy = (((tile_id % 256) // 8) % 16) * TILE
    alpha_paste(dst, src.crop((sx, sy, sx + TILE, sy + TILE)), dx, dy)


def draw_autotile(dst, tile_id, dx, dy, bitmaps):
    kind = (tile_id - 2048) // 48
    shape = (tile_id - 2048) % 48
    tx = kind % 8
    ty = kind // 8

    if 5888 <= tile_id < 8192:
        set_number = 3
        bx = tx * 2
        by = math.floor((ty - 10) * 2.5 + (0.5 if ty % 2 else 0.0))
        table = WALL_AUTOTILE_TABLE if ty % 2 else FLOOR_AUTOTILE_TABLE
    elif 4352 <= tile_id < 5888:
        set_number = 2
        bx = tx * 2
        by = (ty - 6) * 2
        table = WALL_AUTOTILE_TABLE
    elif 2816 <= tile_id < 4352:
        set_number = 1
        bx = tx * 2
        by = (ty - 2) * 3
        table = FLOOR_AUTOTILE_TABLE
    elif 2048 <= tile_id < 2816:
        # A1 is not used by the first ten maps in NARAKU. Keep an explicit
        # error so later maps don't silently render wrong.
        raise RuntimeError(f"A1 autotile support needed for tile {tile_id}")
    else:
        raise RuntimeError(f"Unsupported autotile: {tile_id}")

    src = bitmaps.get(set_number)
    if src is None:
        raise RuntimeError(f"Missing autotile bitmap #{set_number} for tile {tile_id}")

    half = TILE // 2
    for i, (qsx, qsy) in enumerate(table[shape]):
        sx = (bx * 2 + qsx) * half
        sy = (by * 2 + qsy) * half
        txd = dx + (i % 2) * half
        tyd = dy + (i // 2) * half
        alpha_paste(dst, src.crop((sx, sy, sx + half, sy + half)), txd, tyd)


def render_tile(tile_id, bitmaps):
    dst = Image.new("RGBA", (TILE, TILE), (0, 0, 0, 0))
    if not (0 < tile_id < 8192):
        return dst
    if tile_id >= 2048:
        draw_autotile(dst, tile_id, 0, 0, bitmaps)
    else:
        draw_normal_tile(dst, tile_id, 0, 0, bitmaps)
    return dst


def paste_with_gutter(atlas, tile, x, y):
    w, h = tile.size
    atlas.alpha_composite(tile, (x + 1, y + 1))
    atlas.paste(tile.crop((0, 0, w, 1)), (x + 1, y))
    atlas.paste(tile.crop((0, h - 1, w, h)), (x + 1, y + h + 1))
    atlas.paste(tile.crop((0, 0, 1, h)), (x, y + 1))
    atlas.paste(tile.crop((w - 1, 0, w, h)), (x + w + 1, y + 1))
    atlas.putpixel((x, y), tile.getpixel((0, 0)))
    atlas.putpixel((x + w + 1, y), tile.getpixel((w - 1, 0)))
    atlas.putpixel((x, y + h + 1), tile.getpixel((0, h - 1)))
    atlas.putpixel((x + w + 1, y + h + 1), tile.getpixel((w - 1, h - 1)))


def rgba8888_bytes(img: Image.Image) -> bytes:
    return img.convert("RGBA").tobytes()


def layered_ids(map_data, x, y):
    w = map_data["width"]
    h = map_data["height"]
    raw = map_data["data"]
    return [raw[(z * h + y) * w + x] for z in (3, 2, 1, 0)]


def check_passage(map_data, flags, x, y, bit):
    for tile_id in layered_ids(map_data, x, y):
        if tile_id <= 0:
            continue
        flag = flags[tile_id]
        if flag & 0x10:
            continue
        if (flag & bit) == 0:
            return True
        if (flag & bit) == bit:
            return False
    return False


def can_pass(map_data, flags, x, y, bit, dx, dy, reverse_bit):
    w = map_data["width"]
    h = map_data["height"]
    nx, ny = x + dx, y + dy
    if nx < 0 or ny < 0 or nx >= w or ny >= h:
        return False
    return check_passage(map_data, flags, x, y, bit) and check_passage(map_data, flags, nx, ny, reverse_bit)


def build_pass_mask(map_data, flags, x, y):
    mask = 0
    if can_pass(map_data, flags, x, y, 0x01, 0, 1, 0x08): mask |= 0x01
    if can_pass(map_data, flags, x, y, 0x02, -1, 0, 0x04): mask |= 0x02
    if can_pass(map_data, flags, x, y, 0x04, 1, 0, 0x02): mask |= 0x04
    if can_pass(map_data, flags, x, y, 0x08, 0, -1, 0x01): mask |= 0x08
    return mask



def classify_surface(tile_img):
    rgba = tile_img.convert("RGBA")
    rs = gs = bs = total = 0
    for r, g, b, a in rgba.getdata():
        if a < 32:
            continue
        rs += r; gs += g; bs += b; total += 1
    if total <= 0:
        return 1
    r = rs / total; g = gs / total; b = bs / total
    # Bloody / fleshy floors in NARAKU are strongly red-dominant.
    # Everything else uses the harder stone/metal footstep.
    if r > g * 1.28 and r > b * 1.15 and r > 55:
        return 2
    return 1


def physical_tile_id(map_data, flags, x, y):
    for tile_id in layered_ids(map_data, x, y):
        if tile_id <= 0:
            continue
        if flags[tile_id] & 0x10:
            continue
        return tile_id
    return 0

def find_font() -> Path:
    for p in [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]:
        if p.exists(): return p
    raise RuntimeError("Install CJK font: sudo apt install -y fonts-noto-cjk")


def font_index_for_lang(lang: int) -> int:
    return {0: 0, 1: 0, 2: 2, 3: 3}.get(lang, 0)


def get_font(path: Path, size: int, idx: int):
    try:
        return ImageFont.truetype(str(path), size, index=idx)
    except TypeError:
        return ImageFont.truetype(str(path), size)


def wrap_pixels(draw, text, font, max_width):
    if not text: return [""]
    lines, cur = [], ""
    tokens = re.findall(r"\S+\s*", text) if " " in text else list(text)
    for tok in tokens:
        candidate = cur + tok
        bbox = draw.textbbox((0, 0), candidate.rstrip(), font=font)
        if cur and bbox[2] - bbox[0] > max_width:
            lines.append(cur.rstrip())
            cur = tok.lstrip() if " " in text else tok
        else:
            cur = candidate
    if cur: lines.append(cur.rstrip())
    return lines or [""]


def make_message_texture(lines, font_path: Path, font_idx: int):
    tex = Image.new("RGBA", (DIALOG_TEX_W, DIALOG_TEX_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)
    draw.rounded_rectangle((6, 4, SCREEN_W - 6, DIALOG_VISIBLE_H - 4), radius=8,
                           fill=(10, 10, 14, 224), outline=(210, 210, 220, 235), width=2)
    font = get_font(font_path, 20, font_idx)
    rendered = []
    for source_line in lines:
        rendered.extend(wrap_pixels(draw, source_line, font, SCREEN_W - 48))
    y = 15
    for line in rendered[:3]:
        draw.text((22, y), line, font=font, fill=(255, 255, 255, 255))
        y += 25
    draw.polygon([(449, 72), (463, 72), (456, 82)], fill=(255, 255, 255, 230))
    return tex


def conditions_unconditional(page):
    c = page.get("conditions", {})
    return not any(c.get(k) for k in (
        "switch1Valid", "switch2Valid", "variableValid", "selfSwitchValid", "itemValid", "actorValid"
    ))


def conditions_map1_post_intro(page):
    if conditions_unconditional(page): return True
    c = page.get("conditions", {})
    return (
        c.get("switch1Valid") and c.get("switch1Id") == 3 and
        not c.get("switch2Valid") and not c.get("variableValid") and
        not c.get("selfSwitchValid") and not c.get("itemValid") and not c.get("actorValid")
    )


def choose_base_page(map_id, event):
    chosen = None
    for page in event.get("pages", []):
        if conditions_map1_post_intro(page) if map_id == 1 else conditions_unconditional(page):
            chosen = page
    return chosen


def page_is_simple_text(page):
    codes = [c.get("code", 0) for c in page.get("list", []) if c.get("code", 0)]
    return bool(codes) and all(code in (101, 401) for code in codes)


def localized_lines(page, texts, lang_key):
    out = []
    for cmd in page.get("list", []):
        if cmd.get("code") != 401: continue
        raw = str(cmd.get("parameters", [""])[0])
        def repl(m):
            idx = int(m.group(1))
            if 0 <= idx < len(texts):
                return str(texts[idx].get(lang_key, ""))
            return ""
        raw = re.sub(r"\\I18N\[(\d+)\]", repl, raw)
        raw = raw.replace("\\.", "").replace("\\|", "")
        out.append(raw)
    return out


def has_water_se(page):
    for cmd in page.get("list", []):
        if cmd.get("code") == 250:
            se = cmd.get("parameters", [{}])[0]
            if "水をバシャッとかける1" in str(se.get("name", "")):
                return True
    return False


def transfer_from_page(page):
    tr = None
    for cmd in page.get("list", []):
        if cmd.get("code") == 201:
            tr = cmd.get("parameters", [])
            break
    if not tr or len(tr) < 6 or tr[0] != 0:
        return None
    changes = []
    for cmd in page.get("list", []):
        if cmd.get("code") == 121:
            p = cmd.get("parameters", [])
            if len(p) >= 3 and p[0] == p[1] and len(changes) < 3:
                # RPG Maker: value 0 = ON, 1 = OFF.
                changes.append((int(p[0]), 1 if int(p[2]) == 0 else 0))
    while len(changes) < 3:
        changes.append((0, 0))
    return {
        "dest_map": int(tr[1]), "dest_x": int(tr[2]), "dest_y": int(tr[3]),
        "direction": int(tr[4]), "splash": has_water_se(page), "changes": changes,
    }


def first_unconditional_transfer_page(event):
    for page in event.get("pages", []):
        if conditions_unconditional(page) and page.get("trigger") == 1 and transfer_from_page(page):
            return page
    return None


def is_big_character(name: str) -> bool:
    m = re.match(r"^[!$]+", Path(name).name)
    return bool(m and "$" in m.group(0))


def is_object_character(name: str) -> bool:
    m = re.match(r"^[!$]+", Path(name).name)
    return bool(m and "!" in m.group(0))


def extract_character_frame(img: Image.Image, name: str, index: int, direction: int, pattern: int):
    big = is_big_character(name)
    fw = img.width // (3 if big else 12)
    fh = img.height // (4 if big else 8)
    row = {2: 0, 4: 1, 6: 2, 8: 3}.get(direction, 0)
    pattern = max(0, min(2, int(pattern)))
    if big:
        bx = by = 0
    else:
        bx = (index % 4) * fw * 3
        by = (index // 4) * fh * 4
    x = bx + pattern * fw
    y = by + row * fh
    return img.crop((x, y, x + fw, y + fh))


def shelf_pack(frames):
    # frames: [(key, image), ...], pack with 1px gutter. Returns positions.
    x = y = row_h = 0
    pos = {}
    atlas = Image.new("RGBA", (EVENT_ATLAS_W, EVENT_ATLAS_H), (0, 0, 0, 0))
    for key, frame in frames:
        need_w, need_h = frame.width + 2, frame.height + 2
        if need_w > EVENT_ATLAS_W or need_h > EVENT_ATLAS_H:
            raise RuntimeError(f"Event frame too large: {frame.size}")
        if x + need_w > EVENT_ATLAS_W:
            x = 0
            y += row_h
            row_h = 0
        if y + need_h > EVENT_ATLAS_H:
            raise RuntimeError("Event atlas overflow; split atlas will be needed")
        paste_with_gutter(atlas, frame, x, y)
        pos[key] = (x + 1, y + 1, frame.width, frame.height)
        x += need_w
        row_h = max(row_h, need_h)
    return atlas, pos




# ---------------------------------------------------------------------------
# v0.5.0 runtime font + compact event VM
# ---------------------------------------------------------------------------
FONT_TEX_W = 512
FONT_TEX_H = 512
FONT_CELL_W = 24
FONT_CELL_H = 28
FONT_COLS = FONT_TEX_W // FONT_CELL_W
FONT_ROWS = FONT_TEX_H // FONT_CELL_H
FONT_PER_PAGE = FONT_COLS * FONT_ROWS
FONT_SIZE = 20

VM_SUPPORTED_CODES = {
    0, 101, 401, 121, 122, 123, 230, 201, 250, 126, 241, 242,
    223, 224, 211, 118, 115, 354, 111, 411, 412, 231, 235,
    205, 505, 102, 402, 403, 404, 117, 232
}

VM_OP_END = 0
VM_OP_TEXT = 1
VM_OP_SWITCH = 2
VM_OP_SELF_SWITCH = 3
VM_OP_WAIT = 4
VM_OP_TRANSFER = 5
VM_OP_SE = 6
VM_OP_ITEM = 7
VM_OP_TRANSPARENCY = 8
VM_OP_TINT = 9
VM_OP_FLASH = 10
VM_OP_BGM = 11
VM_OP_FADE_BGM = 12
VM_OP_EXIT = 13
VM_OP_PICTURE6 = 14
VM_OP_VARIABLE = 15
VM_OP_COND_SWITCH = 16
VM_OP_COND_VAR = 17
VM_OP_COND_ITEM = 18
VM_OP_COND_LANG = 19
VM_OP_JUMP = 20
VM_OP_MOVE_ROUTE = 21
VM_OP_CHOICES = 22
VM_OP_COND_CHOICE = 23
VM_OP_COMMON_EVENT = 24
VM_OP_SHOW_PICTURE = 25
VM_OP_MOVE_PICTURE = 26
VM_OP_ERASE_PICTURE = 27

SE_IDS = {
    "【音々亭】bonecrush4": 1,
    "【魔王魂】  水01": 2,
    "【効果音ラボ】水をバシャッとかける1": 3,
}

def localized_string(raw, texts, lang_key):
    raw = str(raw or "")
    def repl(m):
        idx = int(m.group(1))
        if 0 <= idx < len(texts) and isinstance(texts[idx], dict):
            return str(texts[idx].get(lang_key, ""))
        return ""
    raw = re.sub(r"\\I18N\[(\d+)\]", repl, raw)
    return raw.replace("\\.", "").replace("\\|", "")

def collect_font_chars(texts, game):
    chars = set(" ?!0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;+-/%()[]<>_=\n")
    for entry in texts:
        if not isinstance(entry, dict):
            continue
        for key in LANG_KEYS:
            chars.update(str(entry.get(key, "")))
    # Also include direct message/choice strings that may not be I18N-backed.
    for map_id in MAP_IDS:
        mp = game / "data" / f"Map{map_id:03d}.json"
        if not mp.exists():
            continue
        data = read_json(mp)
        for ev in data.get("events", []):
            if not ev:
                continue
            for page in ev.get("pages", []):
                for cmd in page.get("list", []):
                    if cmd.get("code") in (101, 401, 102, 402):
                        for value in cmd.get("parameters", []):
                            if isinstance(value, str):
                                chars.update(re.sub(r"\\I18N\[\d+\]", "", value))
                            elif isinstance(value, list):
                                for value2 in value:
                                    if isinstance(value2, str):
                                        chars.update(re.sub(r"\\I18N\[\d+\]", "", value2))
    # Control characters are not glyphs.
    chars.discard("\r")
    chars.discard("\n")
    chars.discard("\t")
    return sorted(chars, key=ord)

def prepare_runtime_font(game, out, texts, font_path):
    chars = collect_font_chars(texts, game)
    pages = (len(chars) + FONT_PER_PAGE - 1) // FONT_PER_PAGE
    font = get_font(font_path, FONT_SIZE, 0)
    page_imgs = [Image.new("L", (FONT_TEX_W, FONT_TEX_H), 0) for _ in range(pages)]
    records = []

    for gi, ch in enumerate(chars):
        page = gi // FONT_PER_PAGE
        slot = gi % FONT_PER_PAGE
        col = slot % FONT_COLS
        row = slot // FONT_COLS
        x0 = col * FONT_CELL_W
        y0 = row * FONT_CELL_H
        draw = ImageDraw.Draw(page_imgs[page])
        bbox = draw.textbbox((0, 0), ch, font=font)
        gw = max(1, bbox[2] - bbox[0])
        gh = max(1, bbox[3] - bbox[1])
        # Use a common baseline for all characters on the line.
        # Individual bbox-centering shifted capitals and descenders up/down.
        draw.text((x0 + 1, y0), ch, font=font, fill=255)
        try:
            adv = int(round(draw.textlength(ch, font=font))) + 1
        except Exception:
            adv = gw + 1
        adv = max(4, min(FONT_CELL_W - 1, adv))
        records.append((ord(ch), page, slot, adv))

    for i, img in enumerate(page_imgs):
        (out / f"font_page{i}.t8").write_bytes(img.tobytes())
        if i == 0:
            img.save(out / "font_page0_preview.png")

    header = struct.pack(
        "<4sHBBBBH", b"NF30", len(records), pages,
        FONT_CELL_W, FONT_CELL_H, FONT_COLS, FONT_ROWS
    )
    body = bytearray()
    for cp, page, slot, adv in records:
        body += struct.pack("<IBHB", cp, page, slot, adv)
    (out / "font_map.bin").write_bytes(header + body)
    return {"glyphs": len(records), "pages": pages}

def route_supported(route):
    if not isinstance(route, dict):
        return False
    supported = {0,1,2,3,4,13,14,15,16,17,18,19,29,31,32,34,35,36,37,38,39,40}
    for rc in route.get("list", []):
        if int(rc.get("code", 0)) not in supported:
            return False
    return True


def branch_supported(par):
    if not par:
        return False
    typ = int(par[0])
    if typ == 0:  # switch
        return len(par) >= 3
    if typ == 1:  # variable vs constant
        return len(par) >= 5 and int(par[2]) == 0
    if typ == 8:  # item possession
        return len(par) >= 2
    if typ == 12 and len(par) >= 2:
        script = str(par[1])
        return bool(re.fullmatch(r'ConfigManager\.language\(\)\s*===\s*"(?:ja_JP|en_US|zh_CN|zh_TW)"', script))
    return False


def page_vm_supported(page):
    for cmd in page.get("list", []):
        code = int(cmd.get("code", 0))
        par = cmd.get("parameters", [])
        if code not in VM_SUPPORTED_CODES:
            return False
        if code == 111 and not branch_supported(par):
            return False
        if code == 102 and (not par or not isinstance(par[0], list) or not 1 <= len(par[0]) <= 6):
            return False
        if code == 117 and (not par or int(par[0]) < 1):
            return False
        if code == 122:
            if len(par) < 5 or int(par[3]) != 0:  # constant operand only
                return False
        if code == 231:
            if len(par) < 10 or int(par[0]) < 1 or int(par[0]) > 100:
                return False
            if int(par[3]) != 0: return False  # variable coordinates not yet implemented
        if code == 232:
            if len(par) < 13 or int(par[0]) < 1 or int(par[0]) > 100:
                return False
            if int(par[3]) != 0: return False
        if code == 235:
            if not par or int(par[0]) < 1 or int(par[0]) > 100:
                return False
        if code == 205:
            if len(par) < 2 or int(par[0]) < -1 or not route_supported(par[1]):
                return False
            if int(par[0]) >= 0 and any(int(rc.get("code",0)) not in
                    {0,1,2,3,4,15,16,17,18,19,29,37,38} for rc in par[1].get("list", [])):
                return False
        # 505 is a route continuation already represented inside command 205.
    return True


def vm_page_conditions(page):
    c = page.get("conditions", {})
    flags = 0
    sw1 = sw2 = 0
    self_idx = 0
    if c.get("switch1Valid"):
        flags |= 0x01; sw1 = int(c.get("switch1Id", 0))
    if c.get("switch2Valid"):
        flags |= 0x02; sw2 = int(c.get("switch2Id", 0))
    if c.get("selfSwitchValid"):
        flags |= 0x04
        self_idx = max(0, min(3, ord(str(c.get("selfSwitchCh", "A"))[:1] or "A") - ord("A")))
    return flags, sw1, sw2, self_idx


def _patch_u32(buf, pos, value):
    struct.pack_into("<I", buf, pos, int(value))


def _emit_condition(out, par):
    typ = int(par[0])
    if typ == 0:
        # [0, switchId, state], state 0=ON / 1=OFF
        out.append(VM_OP_COND_SWITCH)
        out += struct.pack("<HB", int(par[1]), 1 if int(par[2]) == 0 else 0)
        pos = len(out); out += b"\x00\x00\x00\x00"
        return pos
    if typ == 1:
        # [1, variableId, operandType(0 const), value, operator]
        out.append(VM_OP_COND_VAR)
        out += struct.pack("<HBi", int(par[1]), int(par[4]), int(par[3]))
        pos = len(out); out += b"\x00\x00\x00\x00"
        return pos
    if typ == 8:
        out.append(VM_OP_COND_ITEM)
        out += struct.pack("<H", int(par[1]))
        pos = len(out); out += b"\x00\x00\x00\x00"
        return pos
    if typ == 12:
        script = str(par[1])
        tags = {"en_US":0, "ja_JP":1, "zh_CN":2, "zh_TW":3}
        m = re.search(r'"(en_US|ja_JP|zh_CN|zh_TW)"', script)
        lang = tags[m.group(1)] if m else 0
        out.append(VM_OP_COND_LANG)
        out += struct.pack("<B", lang)
        pos = len(out); out += b"\x00\x00\x00\x00"
        return pos
    raise RuntimeError(f"unsupported branch: {par}")


def compile_vm_commands(page, texts):
    out = bytearray()
    lst = page.get("list", [])
    i = 0
    branch_stack = []
    choice_stack = []
    while i < len(lst):
        cmd = lst[i]
        code = int(cmd.get("code", 0))
        par = cmd.get("parameters", [])
        if code == 0:
            break
        if code == 101:
            speaker_raw = str(par[4]) if len(par) >= 5 else ""
            lines = []
            j = i + 1
            while j < len(lst) and int(lst[j].get("code", 0)) == 401:
                p2 = lst[j].get("parameters", [""])
                lines.append(str(p2[0]) if p2 else "")
                j += 1
            variants = []
            for lkey in LANG_KEYS:
                speaker = localized_string(speaker_raw, texts, lkey).encode("utf-8")
                message = "\n".join(localized_string(x, texts, lkey) for x in lines).encode("utf-8")
                variants.append((speaker, message))
            out.append(VM_OP_TEXT)
            for speaker, message in variants:
                out += struct.pack("<HH", len(speaker), len(message))
            for speaker, message in variants:
                out += speaker + message
            i = j
            continue
        if code in (401, 505):
            i += 1
            continue
        if code == 102:
            opts = par[0]
            n = len(opts)
            cancel = int(par[1]) if len(par) > 1 else -1
            default = int(par[2]) if len(par) > 2 else 0
            out += struct.pack("<BBBB", VM_OP_CHOICES, n, cancel & 255, default & 255)
            for option in opts:
                variants = [localized_string(option, texts, lk).encode("utf-8") for lk in LANG_KEYS]
                out += struct.pack("<4H", *(len(v) for v in variants))
                for v in variants:
                    out += v
            choice_stack.append({"indent": int(cmd.get("indent", 0)),
                                 "last": None, "end_jumps": []})
        elif code in (402, 403):
            if choice_stack:
                ctx = choice_stack[-1]
                if ctx["last"] is not None:
                    out.append(VM_OP_JUMP)
                    end_pos = len(out); out += b"\0\0\0\0"
                    ctx["end_jumps"].append(end_pos)
                    _patch_u32(out, ctx["last"], len(out))
                choice_idx = int(par[0]) if code == 402 and par else 255
                out.append(VM_OP_COND_CHOICE)
                out += struct.pack("<B", choice_idx)
                ctx["last"] = len(out)
                out += b"\0\0\0\0"
        elif code == 404:
            if choice_stack:
                ctx = choice_stack.pop()
                if ctx["last"] is not None: _patch_u32(out, ctx["last"], len(out))
                for pos in ctx["end_jumps"]: _patch_u32(out, pos, len(out))
        elif code == 117 and par:
            out.append(VM_OP_COMMON_EVENT)
            out += struct.pack("<H", int(par[0]))
        elif code == 111:
            false_pos = _emit_condition(out, par)
            branch_stack.append({"false_pos": false_pos, "end_pos": None})
        elif code == 411:
            if branch_stack:
                out.append(VM_OP_JUMP)
                end_pos = len(out); out += b"\x00\x00\x00\x00"
                ctx = branch_stack[-1]
                _patch_u32(out, ctx["false_pos"], len(out))
                ctx["end_pos"] = end_pos
        elif code == 412:
            if branch_stack:
                ctx = branch_stack.pop()
                if ctx["end_pos"] is not None:
                    _patch_u32(out, ctx["end_pos"], len(out))
                else:
                    _patch_u32(out, ctx["false_pos"], len(out))
        elif code == 121 and len(par) >= 3:
            out.append(VM_OP_SWITCH)
            out += struct.pack("<HHB", int(par[0]), int(par[1]), 1 if int(par[2]) == 0 else 0)
        elif code == 122 and len(par) >= 5:
            out.append(VM_OP_VARIABLE)
            out += struct.pack("<HHBi", int(par[0]), int(par[1]), int(par[2]), int(par[4]))
        elif code == 123 and len(par) >= 2:
            out.append(VM_OP_SELF_SWITCH)
            letter = max(0, min(3, ord(str(par[0])[:1] or "A") - ord("A")))
            out += struct.pack("<BB", letter, 1 if int(par[1]) == 0 else 0)
        elif code == 230 and par:
            out.append(VM_OP_WAIT); out += struct.pack("<H", max(0, min(65535, int(par[0]))))
        elif code == 201 and len(par) >= 6 and int(par[0]) == 0:
            out.append(VM_OP_TRANSFER)
            out += struct.pack("<HHHBB", int(par[1]), int(par[2]), int(par[3]), int(par[4]), int(par[5]))
        elif code == 250 and par and isinstance(par[0], dict):
            a = par[0]; name = str(a.get("name", ""))
            out.append(VM_OP_SE)
            out += struct.pack("<HBBB", SE_IDS.get(name, 0), int(a.get("volume", 90)), int(a.get("pitch", 100)), int(a.get("pan", 0)) + 100)
        elif code == 126 and len(par) >= 4:
            amount = int(par[3]) if int(par[2]) == 0 else 0
            if int(par[1]) == 1: amount = -amount
            out.append(VM_OP_ITEM); out += struct.pack("<Hh", int(par[0]), amount)
        elif code == 211 and par:
            out.append(VM_OP_TRANSPARENCY); out += struct.pack("<B", 1 if int(par[0]) else 0)
        elif code == 223 and len(par) >= 3:
            tone = list(par[0]) + [0,0,0,0]
            out.append(VM_OP_TINT)
            out += struct.pack("<hhhhHB", int(tone[0]), int(tone[1]), int(tone[2]), int(tone[3]), int(par[1]), 1 if par[2] else 0)
        elif code == 224 and len(par) >= 3:
            color = list(par[0]) + [0,0,0,0]
            out.append(VM_OP_FLASH)
            out += struct.pack("<hhhhHB", int(color[0]), int(color[1]), int(color[2]), int(color[3]), int(par[1]), 1 if par[2] else 0)
        elif code == 241 and par and isinstance(par[0], dict):
            a = par[0]; name = str(a.get("name", ""))
            out.append(VM_OP_BGM)
            out += struct.pack("<HBBB", 1 if name == "【SE音人】街独特の低音" else 0, int(a.get("volume",90)), int(a.get("pitch",100)), int(a.get("pan",0))+100)
        elif code == 242 and par:
            out.append(VM_OP_FADE_BGM); out += struct.pack("<H", int(par[0]))
        elif code == 231:
            num, name, origin, pos_type, x, y, sx, sy, opacity, blend = par[:10]
            num = int(num)
            if num == 6 and str(name) == "A1":
                out.append(VM_OP_PICTURE6); out += b"\x01"
            else:
                rid = PICTURE_IDS.get(str(name), 0)
                out.append(VM_OP_SHOW_PICTURE)
                out += struct.pack("<HHBiiBBB",num,rid,int(origin),int(x),int(y),
                                   max(0,min(255,int(sx))),max(0,min(255,int(sy))),max(0,min(255,int(opacity))))
        elif code == 232:
            num, origin, pos_type, coord_type, x, y, sx, sy, opacity, blend, duration, wait, easing = par[:13]
            out.append(VM_OP_MOVE_PICTURE)
            out += struct.pack("<HiiBBBHB",int(num),int(x),int(y),
                               max(0,min(255,int(sx))),max(0,min(255,int(sy))),
                               max(0,min(255,int(opacity))),max(0,min(65535,int(duration))),1 if wait else 0)
            out += b"\0"  # reserved
        elif code == 235:
            num = int(par[0])
            if num == 6:
                out.append(VM_OP_PICTURE6);out+=b"\0"
            else:
                out.append(VM_OP_ERASE_PICTURE)
                out += struct.pack("<H",num)
        elif code == 205 and len(par) >= 2:
            route = par[1]
            route_cmds = [r for r in route.get("list", []) if int(r.get("code",0)) != 0]
            out.append(VM_OP_MOVE_ROUTE)
            out += struct.pack("<hH", int(par[0]), len(route_cmds))
            for rc in route_cmds:
                rcode = int(rc.get("code",0))
                rp = rc.get("parameters", []) or []
                p1 = int(rp[0]) if len(rp) > 0 and isinstance(rp[0], (int,float)) else 0
                p2 = int(rp[1]) if len(rp) > 1 and isinstance(rp[1], (int,float)) else 0
                out += struct.pack("<Bhh", rcode, p1, p2)
        elif code in (115, 354):
            out.append(VM_OP_EXIT)
        # labels / comments are no-ops
        i += 1

    while choice_stack:
        ctx = choice_stack.pop()
        if ctx["last"] is not None: _patch_u32(out, ctx["last"], len(out))
        for pos in ctx["end_jumps"]: _patch_u32(out, pos, len(out))
    while branch_stack:
        ctx = branch_stack.pop()
        if ctx["end_pos"] is not None:
            _patch_u32(out, ctx["end_pos"], len(out))
        else:
            _patch_u32(out, ctx["false_pos"], len(out))
    out.append(VM_OP_END)
    return bytes(out)


def prepare_picture_assets(game, out, key):
    global PICTURE_IDS
    refs = set()
    for map_id in MAP_IDS:
        mp = read_json(game / "data" / f"Map{map_id:03d}.json")
        for ev in mp.get("events", []):
            if not ev: continue
            for pg in ev.get("pages", []):
                for cmd in pg.get("list", []):
                    if cmd.get("code") == 231 and len(cmd.get("parameters", [])) >= 2:
                        num, name = cmd["parameters"][:2]
                        if name and not (int(num) == 6 and name == "A1"):
                            refs.add(str(name))
    for ce in read_json(game / "data" / "CommonEvents.json"):
        if not ce: continue
        for cmd in ce.get("list", []):
            if cmd.get("code") == 231 and len(cmd.get("parameters", [])) >= 2:
                num, name = cmd["parameters"][:2]
                if name and not (int(num) == 6 and name == "A1"):
                    refs.add(str(name))
    PICTURE_IDS = {name:i+1 for i,name in enumerate(sorted(refs))}
    missing = []
    for name, rid in PICTURE_IDS.items():
        enc = game / "img" / "pictures" / (name + ".png_")
        plain = game / "img" / "pictures" / (name + ".png")
        dst = out / f"pic_{rid:03d}.p44"
        if dst.exists() and dst.stat().st_size == 8 + 512*512*2:
            continue
        if enc.is_file(): image = load_encrypted_png(enc, key)
        elif plain.is_file(): image = Image.open(plain).convert("RGBA")
        else:
            missing.append(name)
            continue
        w = max(1, int(round(image.width * 0.5)))
        h = max(1, int(round(image.height * 0.5)))
        image = image.resize((w,h), Image.Resampling.LANCZOS)
        if w > 512 or h > 512:
            image.thumbnail((512,512), Image.Resampling.LANCZOS)
        w,h = image.size
        sheet = Image.new("RGBA", (512,512), (0,0,0,0))
        sheet.paste(image,(0,0))
        rgba = sheet.tobytes()
        packed = bytearray(512*512*2)
        for i in range(0,len(rgba),4):
            color = (rgba[i]>>4) | ((rgba[i+1]>>4)<<4) | ((rgba[i+2]>>4)<<8) | ((rgba[i+3]>>4)<<12)
            packed[i//2] = color & 255
            packed[i//2+1] = (color>>8) & 255
        dst.write_bytes(struct.pack("<4sHH",b"NP50",w,h)+packed)
    if missing:
        raise RuntimeError("Missing picture resources: " + repr(missing[:15]))
    (out / "picture_v050_manifest.json").write_text(
        json.dumps(PICTURE_IDS, ensure_ascii=False, indent=2), encoding="utf-8")
    return len(PICTURE_IDS)


def compile_common_events(game, texts, out):
    common = read_json(game / "data" / "CommonEvents.json")
    if len(common) > 256: raise RuntimeError("Too many Common Events for v0.5")
    base = 8 + len(common) * 8
    records = bytearray()
    codeblob = bytearray()
    supported = 0
    for ce in common:
        commands = ce.get("list", []) if ce else []
        # Transfers inside recursive events need state-machine support not
        # available yet. Reject these events instead of corrupting map buffers.
        safe = ce is not None and page_vm_supported({"list":commands}) and not any(
            int(c.get("code", 0)) == 201 for c in commands)
        if safe:
            code = compile_vm_commands({"list":commands}, texts)
            records += struct.pack("<II", base + len(codeblob), len(code))
            codeblob += code
            supported += 1
        else:
            records += struct.pack("<II", 0, 0)
    raw = struct.pack("<4sHH", b"NC50", len(common), 0) + records + codeblob
    (out / "common_vm.bin").write_bytes(raw)
    return len(common), supported


def compile_map_vm(map_data, texts, out_path):
    events = []
    pages = []
    blob = bytearray()
    supported_pages = 0
    trigger_counts = [0,0,0,0,0]

    for ev in map_data.get("events", []):
        if not ev:
            continue
        first_page = len(pages)
        ev_pages = ev.get("pages", [])
        for page in ev_pages:
            flags, sw1, sw2, self_idx = vm_page_conditions(page)
            supported = page_vm_supported(page)
            cmd_off = len(blob)
            code = compile_vm_commands(page, texts) if supported else bytes([VM_OP_END])
            blob += code
            trigger = int(page.get("trigger", 0))
            if 0 <= trigger < len(trigger_counts): trigger_counts[trigger] += 1
            page_flags = 0
            if page.get("through", False): page_flags |= 0x01
            # Mark pages that contain a direct transfer; movement uses this to
            # allow entering narrow transfer cells despite directional flags.
            if any(int(c.get("code",0)) == 201 for c in page.get("list", [])):
                page_flags |= 0x02
            pages.append((
                flags, trigger, int(page.get("priorityType",1)), page_flags,
                sw1, sw2, self_idx, 1 if supported else 0, cmd_off, len(code)
            ))
            if supported: supported_pages += 1
        events.append((int(ev.get("id",0)), int(ev.get("x",0)), int(ev.get("y",0)), first_page, len(ev_pages)))

    header_size = 20
    event_size = 10
    page_size = 20
    cmd_off_abs = header_size + len(events)*event_size + len(pages)*page_size
    raw = bytearray(struct.pack("<4sHHIII", b"NV40", len(events), len(pages), cmd_off_abs, len(blob), 0))
    for e in events:
        raw += struct.pack("<HHHHBB", e[0], e[1], e[2], e[3], e[4], 0)
    for p in pages:
        raw += struct.pack("<BBBBHHBBHII", *p[:8], 0, p[8], p[9])
    raw += blob
    out_path.write_bytes(raw)
    return {"events":len(events), "pages":len(pages), "supported":supported_pages, "triggers":trigger_counts}


def prepare_player_atlas(game, out, key, system, actors):
    actor_id = system["partyMembers"][0]
    actor = actors[actor_id]
    name = actor["characterName"]
    idx = actor["characterIndex"]
    img = load_encrypted_png(game / "img" / "characters" / f"{name}.png_", key)
    fw, fh = img.width // 12, img.height // 8
    bx = (idx % 4) * fw * 3
    by = (idx // 4) * fh * 4
    atlas = Image.new("RGBA", (CHAR_TEX_W, CHAR_TEX_H), (0, 0, 0, 0))
    for row in range(4):
        for col in range(3):
            frame = img.crop((bx + col*fw, by + row*fh, bx + (col+1)*fw, by + (row+1)*fh))
            paste_with_gutter(atlas, frame, col*CHAR_SLOT_W, row*CHAR_SLOT_H)
    (out / "enri_atlas.rgba8888").write_bytes(rgba8888_bytes(atlas))
    atlas.save(out / "enri_atlas_preview.png")
    return fw, fh


def prepare_map(game, out, key, tilesets, texts, font_path, map_id):
    map_data = read_json(game / "data" / f"Map{map_id:03d}.json")
    w, h = map_data["width"], map_data["height"]
    tileset = tilesets[map_data["tilesetId"]]
    flags = tileset["flags"]
    names = tileset["tilesetNames"]

    bitmaps = {}
    for set_number, name in enumerate(names):
        if not name: continue
        src = game / "img" / "tilesets" / f"{name}.png_"
        if src.exists(): bitmaps[set_number] = load_encrypted_png(src, key)

    raw = map_data["data"]
    unique_ids = sorted({
        raw[(z*h+y)*w+x]
        for z in range(4) for y in range(h) for x in range(w)
        if raw[(z*h+y)*w+x] > 0
    })
    if len(unique_ids) > 300:
        raise RuntimeError(
            f"Map{map_id:03d} uses {len(unique_ids)} unique tiles; "
            "v0.5.0 supports up to 300 tiles/map"
        )

    tile_to_slot = {tile_id: i + 1 for i, tile_id in enumerate(unique_ids)}
    atlas_count = max(1, (len(unique_ids) + 99) // 100)
    atlases = [
        Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
        for _ in range(atlas_count)
    ]
    rendered_tiles = {}
    for tile_id, slot in tile_to_slot.items():
        idx = slot - 1
        atlas_index = idx // 100
        local_index = idx % 100
        tile_img = render_tile(tile_id, bitmaps)
        rendered_tiles[tile_id] = tile_img
        paste_with_gutter(
            atlases[atlas_index],
            tile_img,
            (local_index % ATLAS_COLS) * ATLAS_SLOT,
            (local_index // ATLAS_COLS) * ATLAS_SLOT,
        )
    for atlas_index, atlas in enumerate(atlases):
        (out / f"map{map_id:03d}_atlas{atlas_index}.rgba8888").write_bytes(
            rgba8888_bytes(atlas)
        )

    layer_words = []
    for z in range(4):
        for y in range(h):
            for x in range(w):
                tile_id = raw[(z*h+y)*w+x]
                if tile_id <= 0:
                    layer_words.append(0)
                else:
                    slot = tile_to_slot[tile_id]
                    if flags[tile_id] & 0x10: slot |= 0x8000
                    layer_words.append(slot)
    pass_masks = bytes(build_pass_mask(map_data, flags, x, y) for y in range(h) for x in range(w))
    surface_types = bytearray(w * h)
    for y in range(h):
        for x in range(w):
            tid = physical_tile_id(map_data, flags, x, y)
            if tid > 0 and tid in rendered_tiles:
                surface_types[y*w+x] = classify_surface(rendered_tiles[tid])
            else:
                surface_types[y*w+x] = 1
    start_x = 0
    start_y = 0
    header = struct.pack("<4s8H", b"NM40", w, h, PSP_TILE, start_x, start_y, len(unique_ids), 0, 0)
    body = b"".join(struct.pack("<H", v) for v in layer_words) + pass_masks + bytes(surface_types)
    (out / f"map{map_id:03d}.bin").write_bytes(header + body)

    # Event compilation.
    action_ids = [0] * (w*h)
    step_flags = bytearray(w*h)
    transfer_indices = bytearray(w*h)
    event_blocks = bytearray(w*h)
    transfers = []
    sprite_defs = []
    sprite_frames = []
    char_cache = {}

    for ev in map_data.get("events", []):
        if not ev: continue
        ex, ey = int(ev["x"]), int(ev["y"])
        if not (0 <= ex < w and 0 <= ey < h): continue

        base_page = choose_base_page(map_id, ev)
        if base_page:
            if base_page.get("trigger") == 1 and has_water_se(base_page):
                step_flags[ey*w+ex] |= 0x01

            imgdef = base_page.get("image", {})
            cname = str(imgdef.get("characterName", ""))
            if cname:
                src = game / "img" / "characters" / f"{cname}.png_"
                if src.exists():
                    if cname not in char_cache:
                        char_cache[cname] = load_encrypted_png(src, key)
                    frame = extract_character_frame(
                        char_cache[cname], cname, int(imgdef.get("characterIndex", 0)),
                        int(imgdef.get("direction", 2)), int(imgdef.get("pattern", 1))
                    )
                    # Event sprites are rendered at half RPG Maker scale on PSP.
                    # Store them already downscaled: this saves RAM/atlas space and
                    # also allows very large one-sheet event graphics to fit 512x512.
                    frame = frame.resize(
                        (max(1, (frame.width + 1) // 2), max(1, (frame.height + 1) // 2)),
                        Image.Resampling.NEAREST,
                    )
                    fkey = (cname, int(imgdef.get("characterIndex", 0)), int(imgdef.get("direction", 2)), int(imgdef.get("pattern", 1)))
                    sprite_frames.append((fkey, frame))
                    priority = int(base_page.get("priorityType", 1))
                    through = bool(base_page.get("through", False))
                    if priority == 1 and not through:
                        event_blocks[ey*w+ex] = 1
                    sprite_defs.append({
                        "event_id": int(ev["id"]), "x": ex, "y": ey, "key": fkey,
                        "priority": priority, "object": is_object_character(cname),
                    })

        tpage = first_unconditional_transfer_page(ev)
        if tpage:
            tr = transfer_from_page(tpage)
            if tr:
                if len(transfers) >= 255:
                    raise RuntimeError("Too many transfers on one map")
                transfers.append(tr)
                transfer_indices[ey*w+ex] = len(transfers)

    # Deduplicate sprite frames while preserving order.
    dedup = []
    seen = set()
    for key2, frame in sprite_frames:
        if key2 not in seen:
            seen.add(key2); dedup.append((key2, frame))
    if dedup:
        ev_atlas, positions = shelf_pack(dedup)
        (out / f"map{map_id:03d}_event_atlas.rgba8888").write_bytes(rgba8888_bytes(ev_atlas))
        ev_atlas.save(out / f"map{map_id:03d}_event_atlas_preview.png")
    else:
        positions = {}

    # Event binary header + cell maps + transfer records + sprite records.
    ev_header = struct.pack("<4s5H", b"NE10", w, h, len(transfers), len(sprite_defs), 0)
    action_raw = b"".join(struct.pack("<H", v) for v in action_ids)
    transfer_raw = bytearray()
    for tr in transfers:
        ch = tr["changes"]
        transfer_raw += struct.pack(
            "<HHHBBHBBHBBHBB",
            tr["dest_map"], tr["dest_x"], tr["dest_y"], tr["direction"], 1 if tr["splash"] else 0,
            ch[0][0], ch[0][1], 0,
            ch[1][0], ch[1][1], 0,
            ch[2][0], ch[2][1], 0,
        )
    sprite_raw = bytearray()
    for sp in sprite_defs:
        sx, sy, sw, sh = positions[sp["key"]]
        flags2 = 1 if sp["object"] else 0
        sprite_raw += struct.pack(
            "<HHHHHHBBH",
            sp["x"], sp["y"], sx, sy, sw, sh,
            sp["priority"], flags2, sp["event_id"]
        )
    (out / f"map{map_id:03d}_events.bin").write_bytes(
        ev_header + action_raw + bytes(step_flags) + bytes(transfer_indices) + bytes(event_blocks) + transfer_raw + sprite_raw
    )

    vm_info = compile_map_vm(map_data, texts, out / f"map{map_id:03d}_vm.bin")

    return {
        "map": map_id, "size": [w, h], "unique_tiles": len(unique_ids), "atlases": atlas_count,
        "actions": 0, "transfers": len(transfers),
        "sprites": len(sprite_defs), "blocks": sum(1 for x in event_blocks if x),
        "vm_pages": vm_info["pages"], "vm_supported": vm_info["supported"],
    }


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU PSP v0.5.0 world (Maps 001-139 + event VM + runtime font + surfaces)")
    ap.add_argument("game", type=Path)
    ap.add_argument("--out", type=Path, default=Path("assets"))
    args = ap.parse_args()
    game = args.game.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    system = read_json(game / "data" / "System.json")
    tilesets = read_json(game / "data" / "Tilesets.json")
    actors = read_json(game / "data" / "Actors.json")
    texts = read_json(game / "data" / "I18NTexts.json")
    key = bytes.fromhex(system.get("encryptionKey", ""))
    if len(key) != 16: raise RuntimeError("Unexpected encryption key")
    font = find_font()

    fw, fh = prepare_player_atlas(game, out, key, system, actors)
    font_info = prepare_runtime_font(game, out, texts, font)
    picture_count = prepare_picture_assets(game, out, key)
    print(f"Pictures prepared: {picture_count}")
    common_total, common_supported = compile_common_events(game, texts, out)
    print(f"Common Events: {common_supported}/{common_total} compiled")
    print(f"Runtime font: {font_info['glyphs']} glyphs, {font_info['pages']} T8 pages")
    manifest = []
    for map_id in MAP_IDS:
        info = prepare_map(game, out, key, tilesets, texts, font, map_id)
        manifest.append(info)
        print(
            f"Map{map_id:03d}: {info['size'][0]}x{info['size'][1]}, "
            f"tiles={info['unique_tiles']}, atlases={info['atlases']}, actions={info['actions']}, "
            f"transfers={info['transfers']}, sprites={info['sprites']}, vm={info['vm_supported']}/{info['vm_pages']}"
        )

    (out / "world_v050_manifest.json").write_text(
        json.dumps({"maps": manifest, "player_frame": [fw, fh], "font": font_info}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print("\nNARAKU PSP v0.5.0 world prepared: Maps 001-139")
    print("Player atlas refreshed; existing intro/audio assets are left untouched.")


if __name__ == "__main__":
    main()
