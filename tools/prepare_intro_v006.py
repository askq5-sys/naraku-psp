#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from PIL import Image

SCREEN_W = 480
SCREEN_H = 272
TEX_W = 512
TEX_H = 512
HALF_W = 408   # 816 / 2
HALF_H = 312   # 624 / 2
CROP_Y = (HALF_H - SCREEN_H) // 2

OPENING1 = {
    0: "オープニング1.png_",              # English
    1: "オープニング1（日本語）.png_",    # Japanese
    2: "オープニング（簡体文字）.png_",   # Simplified Chinese
    3: "オープニング（繁体文字）.png_",   # Traditional Chinese
}
OPENING2_EN = "オープニング2（英語）.png_"
OPENING2_DEFAULT = "オープニング2.png_"
BGM_NAME = "【SE音人】街独特の低音.ogg_"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def decrypt_mz(path: Path, key: bytes) -> bytes:
    raw = path.read_bytes()
    if len(raw) < 32:
        raise RuntimeError(f"Encrypted resource is too small: {path}")
    body = bytearray(raw[16:])
    for i in range(16):
        body[i] ^= key[i]
    return bytes(body)


def load_encrypted_png(path: Path, key: bytes) -> Image.Image:
    import io
    data = decrypt_mz(path, key)
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    if im.size != (816, 624):
        print(f"warning: {path.name}: expected 816x624, got {im.size}")
    return im


def make_psp_screen_texture(im: Image.Image) -> Image.Image:
    # Keep the exact 1/2 scale used by the 24 px tile renderer.
    # 816x624 -> 408x312, then crop 20 px from top/bottom to PSP's 272 px height.
    half = im.resize((HALF_W, HALF_H), Image.Resampling.LANCZOS)
    crop = half.crop((0, CROP_Y, HALF_W, CROP_Y + SCREEN_H))
    screen = Image.new("RGBA", (SCREEN_W, SCREEN_H), (0, 0, 0, 255))
    screen.alpha_composite(crop, ((SCREEN_W - HALF_W) // 2, 0))

    tex = Image.new("RGBA", (TEX_W, TEX_H), (0, 0, 0, 0))
    tex.alpha_composite(screen, (0, 0))
    return tex


def write_rgba8888(path: Path, tex: Image.Image):
    path.write_bytes(tex.convert("RGBA").tobytes())


def prepare_picture(src: Path, dst: Path, preview: Path, key: bytes):
    im = load_encrypted_png(src, key)
    tex = make_psp_screen_texture(im)
    write_rgba8888(dst, tex)
    tex.crop((0, 0, SCREEN_W, SCREEN_H)).save(preview)
    print(f"picture: {src.name} -> {dst.name} ({dst.stat().st_size} bytes)")


def run_ffmpeg_pcm(ogg_bytes: bytes, out_path: Path, pitch: int, volume: int):
    # PSP audio output is 44.1 kHz signed 16-bit interleaved stereo.
    # Bake RPG Maker pitch into the PCM so the PSP runtime does no resampling.
    with tempfile.TemporaryDirectory(prefix="naraku_psp_audio_") as td:
        td = Path(td)
        src = td / "src.ogg"
        src.write_bytes(ogg_bytes)
        pitch_ratio = pitch / 100.0
        af = (
            f"aresample=44100,"
            f"asetrate={44100.0 * pitch_ratio:.3f},"
            f"aresample=44100,"
            f"volume={volume / 100.0:.6f}"
        )
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(src),
            "-af", af,
            "-ac", "2", "-ar", "44100",
            "-f", "s16le", str(out_path),
        ]
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found. Install it with: sudo apt install -y ffmpeg")
        except subprocess.CalledProcessError as exc:
            raise RuntimeError(f"ffmpeg failed with exit code {exc.returncode}") from exc


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU PSP 0.0.6 intro pictures and BGM")
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
    bgm = game / "audio" / "bgm"

    lang_names = ["en", "ja", "zhcn", "zhtw"]
    for lang, src_name in OPENING1.items():
        tag = lang_names[lang]
        prepare_picture(
            pictures / src_name,
            out / f"opening1_{tag}.rgba8888",
            out / f"opening1_{tag}_preview.png",
            key,
        )

    prepare_picture(
        pictures / OPENING2_EN,
        out / "opening2_en.rgba8888",
        out / "opening2_en_preview.png",
        key,
    )
    prepare_picture(
        pictures / OPENING2_DEFAULT,
        out / "opening2_default.rgba8888",
        out / "opening2_default_preview.png",
        key,
    )

    bgm_src = bgm / BGM_NAME
    pcm_path = out / "bgm_low.pcm"
    run_ffmpeg_pcm(decrypt_mz(bgm_src, key), pcm_path, pitch=60, volume=80)
    seconds = pcm_path.stat().st_size / (44100 * 2 * 2)
    print(f"BGM: {BGM_NAME} -> {pcm_path.name} ({pcm_path.stat().st_size} bytes, {seconds:.2f}s PCM)")

    meta = {
        "version": "0.0.6",
        "languages": ["en_US", "ja_JP", "zh_CN", "zh_TW"],
        "screen": [SCREEN_W, SCREEN_H],
        "virtual_half_scale": [HALF_W, HALF_H],
        "crop_y": CROP_Y,
        "bgm": {"source": BGM_NAME, "volume": 80, "pitch": 60, "loop": True},
    }
    (out / "intro_v006_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("\nNARAKU PSP 0.0.6 intro assets ready.")


if __name__ == "__main__":
    main()
