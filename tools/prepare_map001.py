#!/usr/bin/env python3
import argparse
import json
import math
import struct
from pathlib import Path
from PIL import Image

TILE = 48
PSP_TILE = 21
MAP_TEX_W = 512
MAP_TEX_H = 512
CHAR_TEX_W = 64
CHAR_TEX_H = 256

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
    import io
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

    if 5888 <= tile_id < 8192:  # A4 -- what Map001 uses
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
        raise RuntimeError(
            f"Map001 unexpectedly uses unsupported A1 autotile {tile_id}. "
            "This 0.0.4 converter intentionally supports Map001's tile types only."
        )

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


def draw_tile(dst, tile_id, dx, dy, bitmaps):
    if not (0 < tile_id < 8192):
        return
    if tile_id >= 2048:
        draw_autotile(dst, tile_id, dx, dy, bitmaps)
    else:
        draw_normal_tile(dst, tile_id, dx, dy, bitmaps)


def image_to_rgba4444(img: Image.Image) -> bytes:
    img = img.convert("RGBA")
    out = bytearray(img.width * img.height * 2)
    j = 0
    for r, g, b, a in img.getdata():
        # GU_PSM_4444: 0xABGR on PSP; little-endian 16-bit words.
        value = ((a >> 4) << 12) | ((b >> 4) << 8) | ((g >> 4) << 4) | (r >> 4)
        out[j:j+2] = struct.pack("<H", value)
        j += 2
    return bytes(out)


def pad_texture(img, width, height):
    if img.width > width or img.height > height:
        raise RuntimeError(f"Image {img.size} does not fit texture {width}x{height}")
    tex = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    tex.alpha_composite(img, (0, 0))
    return tex


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU Map001 for NARAKU PSP 0.0.4")
    ap.add_argument("game", type=Path, help="Path to installed NARAKU directory")
    ap.add_argument("--out", type=Path, default=Path("assets"), help="Output assets directory")
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

    key_hex = system.get("encryptionKey", "")
    key = bytes.fromhex(key_hex)
    if len(key) != 16:
        raise RuntimeError(f"Unexpected encryption key length: {len(key)}")

    tileset = tilesets[map_data["tilesetId"]]
    names = tileset["tilesetNames"]
    flags = tileset["flags"]

    # RPG Maker set numbers 0..8 are A1,A2,A3,A4,A5,B,C,D,E.
    bitmaps = {}
    for set_number, name in enumerate(names):
        if not name:
            continue
        src = img_dir / "tilesets" / f"{name}.png_"
        if src.exists():
            bitmaps[set_number] = load_encrypted_png(src, key)
            print(f"tileset[{set_number}] {name}: {bitmaps[set_number].size}")

    mw = map_data["width"]
    mh = map_data["height"]
    raw = map_data["data"]
    original_size = (mw * TILE, mh * TILE)
    lower = Image.new("RGBA", original_size, (0, 0, 0, 0))
    upper = Image.new("RGBA", original_size, (0, 0, 0, 0))

    for y in range(mh):
        for x in range(mw):
            for z in range(4):
                tile_id = raw[(z * mh + y) * mw + x]
                if not tile_id:
                    continue
                dst = upper if (flags[tile_id] & 0x10) else lower
                draw_tile(dst, tile_id, x * TILE, y * TILE, bitmaps)

    scaled_size = (mw * PSP_TILE, mh * PSP_TILE)
    lower_s = lower.resize(scaled_size, Image.Resampling.NEAREST)
    upper_s = upper.resize(scaled_size, Image.Resampling.NEAREST)

    # Preview with both map layers.
    preview = Image.new("RGBA", scaled_size, (0, 0, 0, 255))
    preview.alpha_composite(lower_s)
    preview.alpha_composite(upper_s)
    preview.save(out / "map001_preview.png")

    lower_tex = pad_texture(lower_s, MAP_TEX_W, MAP_TEX_H)
    upper_tex = pad_texture(upper_s, MAP_TEX_W, MAP_TEX_H)
    (out / "map001_lower.rgba4444").write_bytes(image_to_rgba4444(lower_tex))
    (out / "map001_upper.rgba4444").write_bytes(image_to_rgba4444(upper_tex))

    # Player: use the starting actor from the party and crop its 3x4 character block.
    actor_id = system["partyMembers"][0]
    actor = actors[actor_id]
    char_name = actor["characterName"]
    char_index = actor["characterIndex"]
    char_img = load_encrypted_png(img_dir / "characters" / f"{char_name}.png_", key)

    pw = char_img.width // 12
    ph = char_img.height // 8
    block_x = (char_index % 4) * pw * 3
    block_y = (char_index // 4) * ph * 4
    block = char_img.crop((block_x, block_y, block_x + pw * 3, block_y + ph * 4))

    frame_w = PSP_TILE
    frame_h = round(ph * (272 / 624))
    char_scaled = block.resize((frame_w * 3, frame_h * 4), Image.Resampling.NEAREST)
    char_tex = pad_texture(char_scaled, CHAR_TEX_W, CHAR_TEX_H)
    (out / "enri.rgba4444").write_bytes(image_to_rgba4444(char_tex))
    char_scaled.save(out / "enri_preview.png")

    meta = {
        "map_id": 1,
        "map_tiles_w": mw,
        "map_tiles_h": mh,
        "tile_px": PSP_TILE,
        "map_px_w": scaled_size[0],
        "map_px_h": scaled_size[1],
        "texture_w": MAP_TEX_W,
        "texture_h": MAP_TEX_H,
        "start_x": system["startX"],
        "start_y": system["startY"],
        "player_frame_w": frame_w,
        "player_frame_h": frame_h,
        "player_texture_w": CHAR_TEX_W,
        "player_texture_h": CHAR_TEX_H,
        "character_name": char_name,
        "character_index": char_index,
    }
    (out / "map001_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\nNARAKU PSP 0.0.4 assets generated:")
    for p in sorted(out.iterdir()):
        print(f"  {p.name:28s} {p.stat().st_size:>8} bytes")
    print(f"\nMap001: {mw}x{mh} tiles -> {scaled_size[0]}x{scaled_size[1]} PSP pixels")
    print(f"Player start: ({system['startX']}, {system['startY']})")
    print(f"Player frame: {frame_w}x{frame_h}")


if __name__ == "__main__":
    main()
