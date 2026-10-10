#!/usr/bin/env python3
import argparse
import io
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SCREEN_W = 480
SCREEN_H = 272
PIC_TEX_W = 512
PIC_TEX_H = 512
HALF_W = 408
HALF_H = 312
CROP_Y = (HALF_H - SCREEN_H) // 2

FALL_TEX_W = 512
FALL_TEX_H = 128
FALL_SLOT_W = 82
FALL_SLOT_H = 82

DIALOG_TEX_W = 512
DIALOG_TEX_H = 128
DIALOG_VISIBLE_H = 96

LANG_TAGS = ["en", "ja", "zhcn", "zhtw"]
LANG_KEYS = ["en_US", "ja_JP", "zh_CN", "zh_TW"]

A1_NAME = "A1.png_"
PORTRAIT_NAME = "エンリ立ち絵.png_"
FALL_CHAR_NAME = "リメイク奈落　キャラチップ　エンリ2.png_"

SE_SPECS = [
    ("【音々亭】bonecrush4.ogg_", "se_bonecrush4.pcm", 70, 40),
    ("【魔王魂】  水01.ogg_", "se_water.pcm", 100, 90),
    ("【効果音ラボ】水をバシャッとかける1.ogg_", "se_splash.pcm", 50, 20),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def decrypt_mz(path: Path, key: bytes) -> bytes:
    raw = path.read_bytes()
    if len(raw) < 32:
        raise RuntimeError(f"Encrypted resource is too small: {path}")
    body = bytearray(raw[16:])
    for i in range(min(16, len(body))):
        body[i] ^= key[i]
    return bytes(body)


def load_encrypted_png(path: Path, key: bytes) -> Image.Image:
    data = decrypt_mz(path, key)
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError(f"Decryption did not produce PNG: {path}")
    return Image.open(io.BytesIO(data)).convert("RGBA")


def rgba8888_bytes(img: Image.Image) -> bytes:
    return img.convert("RGBA").tobytes()


def make_half_screen_texture(im: Image.Image, transparent_background: bool) -> Image.Image:
    half = im.resize((HALF_W, HALF_H), Image.Resampling.LANCZOS)
    crop = half.crop((0, CROP_Y, HALF_W, CROP_Y + SCREEN_H))
    bg = (0, 0, 0, 0) if transparent_background else (0, 0, 0, 255)
    screen = Image.new("RGBA", (SCREEN_W, SCREEN_H), bg)
    screen.alpha_composite(crop, ((SCREEN_W - HALF_W) // 2, 0))
    tex = Image.new("RGBA", (PIC_TEX_W, PIC_TEX_H), (0, 0, 0, 0))
    tex.alpha_composite(screen, (0, 0))
    return tex


def write_picture(src: Path, dst: Path, preview: Path, key: bytes, transparent_background: bool):
    im = load_encrypted_png(src, key)
    tex = make_half_screen_texture(im, transparent_background)
    dst.write_bytes(rgba8888_bytes(tex))
    tex.crop((0, 0, SCREEN_W, SCREEN_H)).save(preview)
    print(f"picture: {src.name} -> {dst.name} ({dst.stat().st_size} bytes)")


def paste_frame_with_gutter(atlas: Image.Image, frame: Image.Image, x: int, y: int):
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


def build_fall_atlas(game: Path, out: Path, key: bytes):
    map001 = read_json(game / "data" / "Map001.json")
    event = map001["events"][5]
    sheet = load_encrypted_png(game / "img" / "characters" / FALL_CHAR_NAME, key)
    fw = sheet.width // 12
    fh = sheet.height // 8
    if fw + 2 > FALL_SLOT_W or fh + 2 > FALL_SLOT_H:
        raise RuntimeError(f"Falling frame {fw}x{fh} does not fit atlas slot")

    atlas = Image.new("RGBA", (FALL_TEX_W, FALL_TEX_H), (0, 0, 0, 0))
    frames = []
    for slot, page_index in enumerate(range(1, 7)):
        image = event["pages"][page_index]["image"]
        if image["characterName"] != "リメイク奈落　キャラチップ　エンリ2":
            raise RuntimeError(f"Unexpected falling sprite on page {page_index}")
        idx = image["characterIndex"]
        direction = image["direction"]
        pattern = image["pattern"]
        row = {2: 0, 4: 1, 6: 2, 8: 3}[direction]
        block_x = (idx % 4) * fw * 3
        block_y = (idx // 4) * fh * 4
        frame = sheet.crop((
            block_x + pattern * fw,
            block_y + row * fh,
            block_x + (pattern + 1) * fw,
            block_y + (row + 1) * fh,
        ))
        x = slot * FALL_SLOT_W
        paste_frame_with_gutter(atlas, frame, x, 0)
        frames.append({
            "slot": slot,
            "page": page_index,
            "character_index": idx,
            "direction": direction,
            "pattern": pattern,
        })

    (out / "fall_atlas.rgba8888").write_bytes(rgba8888_bytes(atlas))
    atlas.save(out / "fall_atlas_preview.png")
    print(f"fall atlas: {fw}x{fh} source frames, 6 states")
    return fw, fh, frames


def find_noto_font():
    candidates = [
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for p in candidates:
        if p.exists():
            return p
    raise RuntimeError(
        "No suitable font found. Install with: sudo apt install -y fonts-noto-cjk"
    )


def font_index_for_lang(lang: int) -> int:
    # NotoSansCJK TTC ordering: JP, KR, SC, TC, HK on standard Ubuntu package.
    return {0: 0, 1: 0, 2: 2, 3: 3}.get(lang, 0)


def make_dialog_texture(name: str, text: str, font_path: Path, font_index: int) -> Image.Image:
    tex = Image.new("RGBA", (DIALOG_TEX_W, DIALOG_TEX_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(tex)
    draw.rounded_rectangle(
        (6, 4, SCREEN_W - 6, DIALOG_VISIBLE_H - 4),
        radius=8,
        fill=(10, 10, 14, 220),
        outline=(210, 210, 220, 230),
        width=2,
    )
    try:
        name_font = ImageFont.truetype(str(font_path), 18, index=font_index)
        body_font = ImageFont.truetype(str(font_path), 22, index=font_index)
    except TypeError:
        name_font = ImageFont.truetype(str(font_path), 18)
        body_font = ImageFont.truetype(str(font_path), 22)
    draw.text((20, 12), name, font=name_font, fill=(230, 230, 235, 255))
    draw.text((28, 45), text, font=body_font, fill=(255, 255, 255, 255))
    draw.polygon([(449, 72), (463, 72), (456, 82)], fill=(255, 255, 255, 230))
    return tex


def build_dialogs(game: Path, out: Path):
    texts = read_json(game / "data" / "I18NTexts.json")
    font_path = find_noto_font()
    print(f"dialog font: {font_path}")
    for lang in range(4):
        key = LANG_KEYS[lang]
        tag = LANG_TAGS[lang]
        font_idx = font_index_for_lang(lang)
        name1 = texts[990][key]
        text1 = texts[991][key]
        name2 = texts[992][key]
        text2 = texts[993][key]
        for num, name, text in [(1, name1, text1), (2, name2, text2)]:
            tex = make_dialog_texture(name, text, font_path, font_idx)
            raw_path = out / f"dialog{num}_{tag}.rgba8888"
            raw_path.write_bytes(rgba8888_bytes(tex))
            tex.crop((0, 0, SCREEN_W, DIALOG_VISIBLE_H)).save(out / f"dialog{num}_{tag}_preview.png")
            print(f"dialog {num}/{tag}: {name!r} {text!r}")


def run_ffmpeg_pcm(ogg_bytes: bytes, out_path: Path, pitch: int, volume: int):
    with tempfile.TemporaryDirectory(prefix="naraku_psp_se_") as td:
        td = Path(td)
        src = td / "src.ogg"
        src.write_bytes(ogg_bytes)
        ratio = pitch / 100.0
        af = (
            f"aresample=44100,"
            f"asetrate={44100.0 * ratio:.3f},"
            f"aresample=44100,"
            f"volume={volume / 100.0:.6f}"
        )
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(src), "-af", af,
            "-ac", "2", "-ar", "44100", "-f", "s16le", str(out_path),
        ]
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found. Install with: sudo apt install -y ffmpeg")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"ffmpeg failed for {out_path.name}: {exc}") from exc


def build_se(game: Path, out: Path, key: bytes):
    se_dir = game / "audio" / "se"
    for src_name, dst_name, pitch, volume in SE_SPECS:
        pcm = out / dst_name
        run_ffmpeg_pcm(decrypt_mz(se_dir / src_name, key), pcm, pitch, volume)
        seconds = pcm.stat().st_size / (44100 * 2 * 2)
        print(f"SE: {src_name} -> {dst_name} ({seconds:.2f}s)")


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU PSP 0.0.7 opening cutscene assets")
    ap.add_argument("game", type=Path, help="Path to installed NARAKU directory")
    ap.add_argument("--out", type=Path, default=Path("assets"), help="Output asset directory")
    args = ap.parse_args()

    game = args.game.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)

    system = read_json(game / "data" / "System.json")
    key = bytes.fromhex(system.get("encryptionKey", ""))
    if len(key) != 16:
        raise RuntimeError(f"Unexpected encryption key length: {len(key)}")

    pictures = game / "img" / "pictures"
    write_picture(
        pictures / A1_NAME,
        out / "a1_overlay.rgba8888",
        out / "a1_overlay_preview.png",
        key,
        transparent_background=True,
    )
    write_picture(
        pictures / PORTRAIT_NAME,
        out / "enri_portrait.rgba8888",
        out / "enri_portrait_preview.png",
        key,
        transparent_background=True,
    )

    fw, fh, fall_frames = build_fall_atlas(game, out, key)
    build_dialogs(game, out)
    build_se(game, out, key)

    meta = {
        "version": "0.0.7",
        "source_event": "Map001 Event 2",
        "fall_source_frame": [fw, fh],
        "fall_render_frame": [fw // 2, fh // 2],
        "fall_states": fall_frames,
        "dialog_ids": [990, 991, 992, 993],
        "se": [
            {"source": s, "output": d, "pitch": p, "volume": v}
            for s, d, p, v in SE_SPECS
        ],
    }
    (out / "intro_v007_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("\nNARAKU PSP 0.0.7 cutscene assets ready.")


if __name__ == "__main__":
    main()
