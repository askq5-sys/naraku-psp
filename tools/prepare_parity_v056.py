#!/usr/bin/env python3
import argparse, io, json, re, subprocess, tempfile
from pathlib import Path
from PIL import Image

SCREEN_W, SCREEN_H = 480, 272
PIC_W, PIC_H = 512, 512
LUCAS_W, LUCAS_H = 256, 64
LUCAS_SLOT_W = 32


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def decrypt_mz(path: Path, key: bytes) -> bytes:
    raw = path.read_bytes()
    if len(raw) < 32:
        raise RuntimeError(f'Encrypted resource is too small: {path}')
    body = bytearray(raw[16:])
    for i in range(min(16, len(body))):
        body[i] ^= key[i]
    return bytes(body)


def load_png(path: Path, key: bytes) -> Image.Image:
    data = decrypt_mz(path, key)
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise RuntimeError(f'Decryption did not produce PNG: {path}')
    return Image.open(io.BytesIO(data)).convert('RGBA')


def decoded_u_name(name: str) -> str:
    return re.sub(r"#U([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), name)


def resolve_named_file(folder: Path, base_name: str, suffixes=(".png_", ".png")) -> Path:
    for suffix in suffixes:
        direct = folder / (base_name + suffix)
        if direct.is_file():
            return direct
    for item in folder.iterdir():
        if not item.is_file():
            continue
        decoded = decoded_u_name(item.name)
        for suffix in suffixes:
            if decoded == base_name + suffix:
                return item
    raise FileNotFoundError(f"Resource {base_name!r} not found in {folder}")


def write_pcm(game: Path, key: bytes, base_name: str, out_path: Path,
              volume: float = 1.0, pitch: float = 1.0):
    src = resolve_named_file(game / 'audio' / 'se', base_name,
                             suffixes=(".ogg_", ".ogg", ".m4a_", ".m4a"))
    raw = decrypt_mz(src, key) if src.suffix.endswith('_') else src.read_bytes()
    filters = []
    if abs(pitch - 1.0) > 0.001:
        filters.append(f"asetrate=44100*{pitch:.6f}")
        filters.append("aresample=44100")
    if abs(volume - 1.0) > 0.001:
        filters.append(f"volume={volume:.6f}")
    with tempfile.TemporaryDirectory(prefix='naraku061_se_') as td:
        inp = Path(td) / 'in.ogg'
        inp.write_bytes(raw)
        cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(inp)]
        if filters:
            cmd += ["-af", ",".join(filters)]
        cmd += ["-ac", "2", "-ar", "44100", "-f", "s16le", str(out_path)]
        subprocess.run(cmd, check=True)


def write_a1(game: Path, out: Path, key: bytes):
    src = load_png(resolve_named_file(game / 'img' / 'pictures', 'A1'), key)
    if src.size != (816, 624):
        raise RuntimeError(f'Unexpected A1 size {src.size}; expected 816x624')

    # A1 is shown at picture #6, origin top-left, x=0 y=0, zoom 100% in the
    # original 816x624 MZ viewport.  It is a screen-space veil, not a map tile.
    # Therefore on PSP it must cover the complete 480x272 viewport rather than
    # being half-scaled to 408px and leaving 36px transparent bars at each side.
    screen = src.resize((SCREEN_W, SCREEN_H), Image.Resampling.LANCZOS)
    tex = Image.new('RGBA', (PIC_W, PIC_H), (0, 0, 0, 0))
    tex.alpha_composite(screen, (0, 0))
    (out / 'a1_overlay.rgba8888').write_bytes(tex.tobytes())
    screen.save(out / 'a1_overlay_preview.png')
    print('A1: 816x624 screen-space picture -> full PSP 480x272 (no transparent side bars)')



def rgba4444_bytes(image: Image.Image) -> bytes:
    rgba = image.convert('RGBA').tobytes()
    packed = bytearray(len(rgba) // 2)
    j = 0
    for i in range(0, len(rgba), 4):
        value = (
            (rgba[i] >> 4)
            | ((rgba[i + 1] >> 4) << 4)
            | ((rgba[i + 2] >> 4) << 8)
            | ((rgba[i + 3] >> 4) << 12)
        )
        packed[j] = value & 0xFF
        packed[j + 1] = (value >> 8) & 0xFF
        j += 2
    return bytes(packed)


def write_fog_a1(game: Path, out: Path, key: bytes):
    """Prepare Common Event 15's scrolling black vignette.

    Original NARAKU uses picture #7 "フォグA1": a 1632x624 bitmap made from
    two byte-identical 816x624 halves. Common Event 15 shows it at x=-816 and
    moves it to x=0 over 816 frames, then the parallel event repeats. The
    duplicate half makes the reset seamless.

    PSP keeps one 816px period resampled to a 512-texel wrap strip.  main.c
    maps that full 512-texel period across the 480px screen and scrolls the
    texture coordinates by 512/816 texels per rendered frame.  Keeping the
    destination quad fixed avoids the one-pixel stepping/shimmer that appears
    when a semi-transparent fog quad itself is moved at subpixel speed.
    """
    src = load_png(resolve_named_file(game / 'img' / 'pictures', 'フォグA1'), key)
    if src.size != (1632, 624):
        raise RuntimeError(f'Unexpected フォグA1 size {src.size}; expected 1632x624')

    left = src.crop((0, 0, 816, 624))
    right = src.crop((816, 0, 1632, 624))
    if left.tobytes() != right.tobytes():
        raise RuntimeError('フォグA1 is no longer two identical 816px periods')

    screen = left.resize((PIC_W, SCREEN_H), Image.Resampling.LANCZOS)
    tex = Image.new('RGBA', (PIC_W, PIC_H), (0, 0, 0, 0))
    tex.alpha_composite(screen, (0, 0))
    (out / 'fog_a1.rgba8888').write_bytes(tex.tobytes())
    # Keep the old file too so a mixed working tree cannot accidentally break an older build.
    (out / 'fog_a1.rgba4444').write_bytes(rgba4444_bytes(tex))
    screen.save(out / 'fog_a1_preview.png')
    print('Fog A1: Common Event 15 -> 512x272 wrapped UV strip (RGBA8888)')


def extract_standard_frame(sheet: Image.Image, index: int, direction: int, pattern: int) -> Image.Image:
    fw = sheet.width // 12
    fh = sheet.height // 8
    block_x = (index % 4) * 3
    block_y = (index // 4) * 4
    row = {2: 0, 4: 1, 6: 2, 8: 3}[direction]
    x = (block_x + pattern) * fw
    y = (block_y + row) * fh
    return sheet.crop((x, y, x + fw, y + fh))


def write_lucas(game: Path, out: Path, key: bytes):
    name = 'リメイク奈落　キャラチップ　ルーカス死亡'
    sheet = load_png(resolve_named_file(game / 'img' / 'characters', name), key)
    if sheet.size != (576, 624):
        raise RuntimeError(f'Unexpected Lucas sheet size {sheet.size}; expected 576x624')

    specs = [(2,0), (2,1), (2,2), (4,0), (4,1)]
    atlas = Image.new('RGBA', (LUCAS_W, LUCAS_H), (0,0,0,0))
    for i, (direction, pattern) in enumerate(specs):
        fr = extract_standard_frame(sheet, 0, direction, pattern)
        fr = fr.resize(((fr.width + 1)//2, (fr.height + 1)//2), Image.Resampling.NEAREST)
        if fr.size != (24,39):
            raise RuntimeError(f'Unexpected Lucas PSP frame {fr.size}')
        x = i * LUCAS_SLOT_W + 1
        y = 1
        atlas.alpha_composite(fr, (x,y))
        # 1px gutters keep nearest/edge sampling stable on PSP GU.
        atlas.paste(fr.crop((0,0,fr.width,1)), (x,0))
        atlas.paste(fr.crop((0,fr.height-1,fr.width,fr.height)), (x,y+fr.height))
        atlas.paste(fr.crop((0,0,1,fr.height)), (x-1,y))
        atlas.paste(fr.crop((fr.width-1,0,fr.width,fr.height)), (x+fr.width,y))
    (out / 'lucas_fall_atlas.rgba8888').write_bytes(atlas.tobytes())
    atlas.save(out / 'lucas_fall_atlas_preview.png')
    print('Lucas Event45: 5 dynamic page frames -> 256x64 atlas, 24x39 each')

    # Map001 Event39 uses the final left-facing frame after Lucas has fallen.
    corpse_frame = extract_standard_frame(sheet, 0, 4, 2)
    corpse_frame = corpse_frame.resize(((corpse_frame.width + 1)//2, (corpse_frame.height + 1)//2), Image.Resampling.NEAREST)
    if corpse_frame.size != (24,39):
        raise RuntimeError(f'Unexpected Lucas corpse PSP frame {corpse_frame.size}')
    corpse = Image.new('RGBA', (64,64), (0,0,0,0))
    corpse.alpha_composite(corpse_frame, (1,1))
    corpse.paste(corpse_frame.crop((0,0,corpse_frame.width,1)), (1,0))
    corpse.paste(corpse_frame.crop((0,corpse_frame.height-1,corpse_frame.width,corpse_frame.height)), (1,1+corpse_frame.height))
    corpse.paste(corpse_frame.crop((0,0,1,corpse_frame.height)), (0,1))
    corpse.paste(corpse_frame.crop((corpse_frame.width-1,0,corpse_frame.width,corpse_frame.height)), (1+corpse_frame.width,1))
    (out / 'lucas_corpse.rgba8888').write_bytes(corpse.tobytes())
    corpse.save(out / 'lucas_corpse_preview.png')
    print('Lucas Event39: final corpse frame -> 64x64 PSP texture')


def write_v061_audio(game: Path, out: Path, key: bytes):
    write_pcm(game, key, 'Evasion1', out / 'se_evasion1.pcm', 0.90, 1.00)
    write_pcm(game, key, '【SE音人】ネバ！ベチャ', out / 'se_slime_fall.pcm', 0.30, 1.20)
    write_pcm(game, key, '【魔王魂】-SE7', out / 'se_se7.pcm', 0.90, 1.00)

    # Water cue used by the post-two-Green-Key parallel sequence (Map008) and
    # the delayed Map009 cue.  Keep their exact volume/pitch variants.
    water = '【魔王魂】  水01'
    write_pcm(game, key, water, out / 'se_water.pcm', 0.90, 1.00)
    write_pcm(game, key, water, out / 'se_water_70_80.pcm', 0.70, 0.80)
    write_pcm(game, key, water, out / 'se_water_50_80.pcm', 0.50, 0.80)

    # One source SE is reused by NARAKU for the bloody/wet floor.  These are
    # the exact event-side parameters found in the original maps.  Keep them
    # pre-rendered so the PSP audio thread only applies the global SE master
    # volume (default 75), exactly once.
    splash = '【効果音ラボ】水をバシャッとかける1'
    write_pcm(game, key, splash, out / 'se_splash.pcm', 0.20, 0.50)
    write_pcm(game, key, splash, out / 'se_splash_step70.pcm', 0.05, 0.70)
    write_pcm(game, key, splash, out / 'se_splash_step120.pcm', 0.05, 1.20)
    write_pcm(game, key, splash, out / 'se_splash_20_70.pcm', 0.20, 0.70)
    print('0.7.1 event SE: exact blood-step 5%@70/120 + splash variants prepared')


def main():
    ap = argparse.ArgumentParser(description='Prepare NARAKU PSP 0.5.6 parity assets')
    ap.add_argument('game', type=Path)
    ap.add_argument('--out', type=Path, default=Path('assets'))
    args = ap.parse_args()
    game = args.game.resolve(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    system = read_json(game / 'data' / 'System.json')
    key = bytes.fromhex(system.get('encryptionKey',''))
    if len(key) != 16:
        raise RuntimeError('Unexpected encryption key length')
    write_a1(game, out, key)
    write_fog_a1(game, out, key)
    write_lucas(game, out, key)
    write_v061_audio(game, out, key)
    print('NARAKU PSP 0.7.1 parity assets ready.')

if __name__ == '__main__':
    main()
