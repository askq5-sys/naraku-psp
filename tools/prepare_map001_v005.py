#!/usr/bin/env python3
import argparse
import io
import json
import math
import struct
from pathlib import Path
from PIL import Image

TILE = 48
PSP_TILE = 24
ATLAS_W = 512
ATLAS_H = 512
ATLAS_SLOT = 50   # 48 px tile + 1 px gutter on each side
ATLAS_COLS = 10
CHAR_TEX_W = 256
CHAR_TEX_H = 512
CHAR_SLOT_W = 50
CHAR_SLOT_H = 80

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
    [[2,2],[3,2],[2,3],[3,3]], [[0,2],[3,2],[0,3],[3,1]],
    [[2,0],[3,0],[2,3],[3,3]], [[0,0],[3,0],[0,3],[3,3]],
]
# Correct one entry accidentally differing in some old snippets:
WALL_AUTOTILE_TABLE[13] = [[0,2],[3,2],[0,3],[3,3]]


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
    if 1536 <= tile_id < 2048:  # A5
        set_number = 4
    else:                       # B-E
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

    if 5888 <= tile_id < 8192:  # A4 (Map001)
        set_number = 3
        bx = tx * 2
        by = math.floor((ty - 10) * 2.5 + (0.5 if ty % 2 else 0.0))
        table = WALL_AUTOTILE_TABLE if ty % 2 else FLOOR_AUTOTILE_TABLE
    elif 4352 <= tile_id < 5888:  # A3
        set_number = 2
        bx = tx * 2
        by = (ty - 6) * 2
        table = WALL_AUTOTILE_TABLE
    elif 2816 <= tile_id < 4352:  # A2
        set_number = 1
        bx = tx * 2
        by = (ty - 2) * 3
        table = FLOOR_AUTOTILE_TABLE
    else:
        raise RuntimeError(f"Unsupported A1 autotile in Map001: {tile_id}")

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
    """Paste 48x48 tile at x+1,y+1 and duplicate edge pixels into 1 px gutter."""
    atlas.alpha_composite(tile, (x + 1, y + 1))
    atlas.paste(tile.crop((0, 0, TILE, 1)), (x + 1, y))
    atlas.paste(tile.crop((0, TILE - 1, TILE, TILE)), (x + 1, y + TILE + 1))
    atlas.paste(tile.crop((0, 0, 1, TILE)), (x, y + 1))
    atlas.paste(tile.crop((TILE - 1, 0, TILE, TILE)), (x + TILE + 1, y + 1))
    atlas.putpixel((x, y), tile.getpixel((0, 0)))
    atlas.putpixel((x + TILE + 1, y), tile.getpixel((TILE - 1, 0)))
    atlas.putpixel((x, y + TILE + 1), tile.getpixel((0, TILE - 1)))
    atlas.putpixel((x + TILE + 1, y + TILE + 1), tile.getpixel((TILE - 1, TILE - 1)))


def paste_frame_with_gutter(atlas, frame, x, y):
    w, h = frame.size
    atlas.alpha_composite(frame, (x + 1, y + 1))
    atlas.paste(frame.crop((0, 0, w, 1)), (x + 1, y))
    atlas.paste(frame.crop((0, h - 1, w, h)), (x + 1, y + h + 1))
    atlas.paste(frame.crop((0, 0, 1, h)), (x, y + 1))
    atlas.paste(frame.crop((w - 1, 0, w, h)), (x + w + 1, y + 1))
    atlas.putpixel((x, y), frame.getpixel((0, 0)))
    atlas.putpixel((x + w + 1, y), frame.getpixel((w - 1, 0)))
    atlas.putpixel((x, y + h + 1), frame.getpixel((0, h - 1)))
    atlas.putpixel((x + w + 1, y + h + 1), frame.getpixel((w - 1, h - 1)))


def rgba8888_bytes(img: Image.Image) -> bytes:
    # PSP GU_PSM_8888 uses little-endian 0xAABBGGRR, which is byte order R,G,B,A.
    return img.convert("RGBA").tobytes()


def layered_ids(map_data, x, y):
    w = map_data["width"]
    h = map_data["height"]
    raw = map_data["data"]
    return [raw[(z * h + y) * w + x] for z in (3, 2, 1, 0)]


def check_passage(map_data, flags, x, y, bit):
    # Mirrors RPG Maker MZ Game_Map.checkPassage for tile layers (no tile-events yet).
    for tile_id in layered_ids(map_data, x, y):
        if tile_id <= 0:
            continue
        flag = flags[tile_id]
        if flag & 0x10:  # star: no effect on passage
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
    # Same directional bits as RPG Maker tile flags: down=1,left=2,right=4,up=8.
    mask = 0
    if can_pass(map_data, flags, x, y, 0x01, 0, 1, 0x08):
        mask |= 0x01
    if can_pass(map_data, flags, x, y, 0x02, -1, 0, 0x04):
        mask |= 0x02
    if can_pass(map_data, flags, x, y, 0x04, 1, 0, 0x02):
        mask |= 0x04
    if can_pass(map_data, flags, x, y, 0x08, 0, -1, 0x01):
        mask |= 0x08
    return mask


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU Map001 for PSP 0.0.5 tile renderer")
    ap.add_argument("game", type=Path, help="Path to installed NARAKU directory")
    ap.add_argument("--out", type=Path, default=Path("assets"), help="Output directory")
    args = ap.parse_args()

    game = args.game.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    data_dir = game / "data"
    img_dir = game / "img"
    system = read_json(data_dir / "System.json")
    tilesets = read_json(data_dir / "Tilesets.json")
    map_data = read_json(data_dir / "Map001.json")
    actors = read_json(data_dir / "Actors.json")

    key = bytes.fromhex(system.get("encryptionKey", ""))
    if len(key) != 16:
        raise RuntimeError(f"Unexpected encryption key length: {len(key)}")

    tileset = tilesets[map_data["tilesetId"]]
    names = tileset["tilesetNames"]
    flags = tileset["flags"]

    bitmaps = {}
    for set_number, name in enumerate(names):
        if not name:
            continue
        src = img_dir / "tilesets" / f"{name}.png_"
        if src.exists():
            bitmaps[set_number] = load_encrypted_png(src, key)
            print(f"tileset[{set_number}] {name}: {bitmaps[set_number].size}")

    mw, mh = map_data["width"], map_data["height"]
    raw = map_data["data"]

    unique_ids = sorted({
        raw[(z * mh + y) * mw + x]
        for z in range(4)
        for y in range(mh)
        for x in range(mw)
        if raw[(z * mh + y) * mw + x] > 0
    })
    if len(unique_ids) > 100:
        raise RuntimeError(f"Map001 uses {len(unique_ids)} unique tiles; 0.0.5 atlas supports 100")

    tile_to_slot = {tile_id: i + 1 for i, tile_id in enumerate(unique_ids)}
    atlas = Image.new("RGBA", (ATLAS_W, ATLAS_H), (0, 0, 0, 0))
    for tile_id, slot in tile_to_slot.items():
        idx = slot - 1
        ax = (idx % ATLAS_COLS) * ATLAS_SLOT
        ay = (idx // ATLAS_COLS) * ATLAS_SLOT
        paste_with_gutter(atlas, render_tile(tile_id, bitmaps), ax, ay)

    atlas.save(out / "map001_atlas_preview.png")
    (out / "map001_atlas.rgba8888").write_bytes(rgba8888_bytes(atlas))

    # 4 map layers. High bit means RPG Maker star/upper tile.
    layer_words = []
    for z in range(4):
        for y in range(mh):
            for x in range(mw):
                tile_id = raw[(z * mh + y) * mw + x]
                if tile_id <= 0:
                    layer_words.append(0)
                    continue
                slot = tile_to_slot[tile_id]
                if flags[tile_id] & 0x10:
                    slot |= 0x8000
                layer_words.append(slot)

    pass_masks = bytes(build_pass_mask(map_data, flags, x, y) for y in range(mh) for x in range(mw))

    # Map binary: magic, width,height,tile_px,start_x,start_y,tile_count, then layers u16, then pass mask u8.
    header = struct.pack(
        "<4s7H",
        b"NPS5",
        mw,
        mh,
        PSP_TILE,
        system["startX"],
        system["startY"],
        len(unique_ids),
        0,
    )
    body = b"".join(struct.pack("<H", v) for v in layer_words) + pass_masks
    (out / "map001.bin").write_bytes(header + body)

    # Player character: preserve original 48x78 frames, put each frame in its own guttered atlas slot.
    actor_id = system["partyMembers"][0]
    actor = actors[actor_id]
    char_name = actor["characterName"]
    char_index = actor["characterIndex"]
    char_img = load_encrypted_png(img_dir / "characters" / f"{char_name}.png_", key)
    fw = char_img.width // 12
    fh = char_img.height // 8
    if fw + 2 > CHAR_SLOT_W or fh + 2 > CHAR_SLOT_H:
        raise RuntimeError(f"Character frame {fw}x{fh} does not fit {CHAR_SLOT_W}x{CHAR_SLOT_H}")
    block_x = (char_index % 4) * fw * 3
    block_y = (char_index // 4) * fh * 4

    char_atlas = Image.new("RGBA", (CHAR_TEX_W, CHAR_TEX_H), (0, 0, 0, 0))
    for row in range(4):
        for col in range(3):
            frame = char_img.crop((
                block_x + col * fw,
                block_y + row * fh,
                block_x + (col + 1) * fw,
                block_y + (row + 1) * fh,
            ))
            paste_frame_with_gutter(char_atlas, frame, col * CHAR_SLOT_W, row * CHAR_SLOT_H)

    char_atlas.save(out / "enri_atlas_preview.png")
    (out / "enri_atlas.rgba8888").write_bytes(rgba8888_bytes(char_atlas))

    # Human preview at PSP scale, assembled from per-tile atlas data (not a baked runtime texture).
    preview = Image.new("RGBA", (mw * PSP_TILE, mh * PSP_TILE), (0, 0, 0, 255))
    for y in range(mh):
        for x in range(mw):
            for z in range(4):
                tile_id = raw[(z * mh + y) * mw + x]
                if not tile_id:
                    continue
                tile = render_tile(tile_id, bitmaps).resize((PSP_TILE, PSP_TILE), Image.Resampling.BOX)
                preview.alpha_composite(tile, (x * PSP_TILE, y * PSP_TILE))
    preview.save(out / "map001_v005_preview.png")

    meta = {
        "map_id": 1,
        "tiles": [mw, mh],
        "psp_tile_px": PSP_TILE,
        "map_px": [mw * PSP_TILE, mh * PSP_TILE],
        "unique_tiles": len(unique_ids),
        "tile_atlas": [ATLAS_W, ATLAS_H],
        "character_frame_original": [fw, fh],
        "character_frame_psp": [fw // 2, fh // 2],
        "start": [system["startX"], system["startY"]],
    }
    (out / "map001_v005_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nNARAKU PSP 0.0.5 assets generated:")
    for p in sorted(out.iterdir()):
        if p.name.startswith("map001_") or p.name.startswith("enri_"):
            print(f"  {p.name}: {p.stat().st_size} bytes")
    print(f"\nMap001: {mw}x{mh} tiles -> {mw*PSP_TILE}x{mh*PSP_TILE} PSP px")
    print(f"Unique tile images: {len(unique_ids)} (native 48x48 kept in atlas)")
    print(f"Start tile: ({system['startX']}, {system['startY']})")
    print(f"Character source frame: {fw}x{fh}, rendered at {fw//2}x{fh//2}")


if __name__ == "__main__":
    main()
