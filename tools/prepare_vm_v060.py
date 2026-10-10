#!/usr/bin/env python3
"""Fast 0.7.5 migration: rebuild only VM/common-event bytecode and picture table.

The expensive tile/event atlases from 0.5.x are binary-compatible with 0.6.0.
If the existing picture manifest is complete we reuse its IDs; otherwise the
original encrypted picture assets are regenerated from the user's Steam copy.
"""
import argparse, json
from pathlib import Path
import prepare_world_v060 as w


def load_picture_manifest(out: Path):
    candidates = [out / "picture_v050_manifest.json", out / "picture_v060_manifest.json"]
    for p in candidates:
        if not p.is_file():
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not data:
                continue
            for _name, rid in data.items():
                if not isinstance(rid, int) or rid < 1:
                    raise ValueError
                if not (out / f"pic_{rid:03d}.p44").is_file():
                    raise FileNotFoundError
            w.PICTURE_IDS = {str(k): int(v) for k, v in data.items()}
            return p, len(data)
        except Exception:
            pass
    return None, 0



def refresh_gameover_picture_assets(game: Path, out: Path, key: bytes):
    """Tag Game Over pictures for aspect-correct fit inside the 480x272 PSP screen.

    The originals are 816x624 (4:3-ish).  Half-scale assets are 408x312, which
    the old generic picture path deliberately cropped vertically.  NGO1 keeps
    the same pixels but tells the runtime to letterbox/fit them instead.
    """
    import struct
    from PIL import Image
    refreshed = 0
    for name, rid in w.PICTURE_IDS.items():
        if not str(name).startswith("ゲームオーバー"):
            continue
        src = w.resolve_named_file(game / "img" / "pictures", str(name), (".png_", ".png"))
        image = w.load_encrypted_png(src, key) if src.name.endswith(".png_") else Image.open(src).convert("RGBA")
        pw = max(1, int(round(image.width * 0.5)))
        ph = max(1, int(round(image.height * 0.5)))
        image = image.resize((pw, ph), Image.Resampling.LANCZOS)
        if pw > 512 or ph > 512:
            image.thumbnail((512, 512), Image.Resampling.LANCZOS)
        pw, ph = image.size
        sheet = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        sheet.paste(image, (0, 0))
        rgba = sheet.tobytes()
        packed = bytearray(512 * 512 * 2)
        for i in range(0, len(rgba), 4):
            color = ((rgba[i] >> 4) | ((rgba[i+1] >> 4) << 4) |
                     ((rgba[i+2] >> 4) << 8) | ((rgba[i+3] >> 4) << 12))
            packed[i//2] = color & 255
            packed[i//2 + 1] = (color >> 8) & 255
        (out / f"pic_{rid:03d}.p44").write_bytes(struct.pack("<4sHH", b"NGO1", pw, ph) + packed)
        refreshed += 1
    return refreshed


def refresh_key_anim_asset(game: Path, out: Path, key: bytes):
    """Build a tiny dedicated !鍵 animation texture for the early story keys.

    The original sheet uses the direction rows as colours: direction 4 is the
    Red Key on Map005, direction 2 is the Iron Key on Map015, and direction 8
    is the Green Key on Map019.  Keeping these frames outside the map event
    atlas avoids the tiny key disappearing in the early upper-tile pass.
    """
    from PIL import Image

    src = w.resolve_named_file(game / "img" / "characters", "!鍵", (".png_", ".png"))
    sheet = w.load_encrypted_png(src, key) if src.name.endswith(".png_") else Image.open(src).convert("RGBA")
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    directions = (4, 2, 8)  # red, iron, green
    for row, direction in enumerate(directions):
        for pattern in range(3):
            frame = w.extract_character_frame(sheet, "!鍵", 0, direction, pattern)
            frame = frame.resize((24, 24), Image.Resampling.NEAREST)
            canvas.alpha_composite(frame, (pattern * 32, row * 32))
    (out / "key_anim.rgba8888").write_bytes(w.rgba8888_bytes(canvas))
    canvas.save(out / "key_anim_preview.png")
    return 3

def main():
    ap = argparse.ArgumentParser(description="Fast NARAKU PSP 0.7.5 VM migration")
    ap.add_argument("game", type=Path)
    ap.add_argument("--out", type=Path, default=Path("assets"))
    args = ap.parse_args()
    game = args.game.resolve(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)

    texts = w.read_json(game / "data" / "I18NTexts.json")
    system = w.read_json(game / "data" / "System.json")
    key = bytes.fromhex(system.get("encryptionKey", ""))
    if len(key) != 16:
        raise RuntimeError("Unexpected encryption key")

    manifest, picture_count = load_picture_manifest(out)
    if manifest:
        print(f"Picture table reused: {picture_count} resources ({manifest.name})")
    else:
        picture_count = w.prepare_picture_assets(game, out, key)
        print(f"Picture table regenerated: {picture_count} resources")

    gameover_count = refresh_gameover_picture_assets(game, out, key)
    print(f"Game Over pictures tagged for PSP fit: {gameover_count}")
    key_rows = refresh_key_anim_asset(game, out, key)
    print(f"Dedicated story-key animation rows: {key_rows}")

    # Rebuild the runtime font even on the fast path.  0.6.0 omitted glyphs
    # used only by the native Options UI (notably 繁 in 繁體中文).
    font = w.find_font()
    font_info = w.prepare_runtime_font(game, out, texts, font)
    print(f"Runtime font: {font_info['glyphs']} glyphs, {font_info['pages']} T8 pages")

    common_total, common_supported = w.compile_common_events(game, texts, out)
    print(f"Common Events: {common_supported}/{common_total} compiled")

    pages = supported = 0
    dynamic_sprites = 0
    # Story-critical early maps need page-aware event graphics.  Rebuild only
    # their tiny event atlases; the expensive tile atlases remain untouched.
    for map_id in w.MAP_IDS:
        if map_id <= 20:
            info = w.prepare_dynamic_event_assets(game, out, key, texts, map_id)
            pages += info["pages"]; supported += info["supported"]
            dynamic_sprites += info["sprites"]
        else:
            mp = w.read_json(game / "data" / f"Map{map_id:03d}.json")
            info = w.compile_map_vm(mp, texts, out / f"map{map_id:03d}_vm.bin")
            pages += info["pages"]; supported += info["supported"]
    print(f"Map VM pages: {supported}/{pages} compiled")
    print(f"Dynamic early-map page sprites: {dynamic_sprites}")
    print("Fast 0.7.5 VM/font/event migration complete; tile atlases were preserved.")

if __name__ == "__main__":
    main()
