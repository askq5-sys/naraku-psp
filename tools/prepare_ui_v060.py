#!/usr/bin/env python3
import argparse, io, json, re, struct, subprocess, tempfile
from pathlib import Path
from PIL import Image

LANG_KEYS = ["en_US", "ja_JP", "zh_CN", "zh_TW"]
MAX_ITEMS = 128
SCREEN_W, SCREEN_H = 480, 272
PIC_TEX_W = PIC_TEX_H = 512

# UI string ids consumed by main.c
LABEL_SPECS = [
    (50, None),     # 0 Items
    (60, None),     # 1 Key Items
    (90, None),     # 2 Save prompt
    (91, None),     # 3 Load prompt
    (92, None),     # 4 File
    (57, None),     # 5 Settings
    (1058, None),   # 6 Back
    (1054, None),   # 7 Save
    (1055, None),   # 8 Load
    (1056, None),   # 9 Return to title
    (1060, None),   # 10 Cancel
    (64, None),     # 11 New game / Fall to Purgatory
    (65, None),     # 12 Continue
    (80, None),     # 13 Always Dash
    (83, None),     # 14 BGM Volume
    (86, None),     # 15 SE Volume
    (6074, None),   # 16 Window opacity
    (0, None),      # 17 Language (DisplayI18NTexts option)
    (None, ["ON", "ON", "ON", "ON"]),           # 18
    (None, ["OFF", "OFF", "OFF", "OFF"]),       # 19
    (None, ["Empty", "空き", "空", "空"]),       # 20
    (50, None),     # 21 inventory title
    (57, None),     # 22 options title
    (1059, None),   # 23 return title confirmation
    (None, ["Shutdown", "Shutdown", "Shutdown", "Shutdown"]), # 24
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


def decoded_u_name(name: str) -> str:
    return re.sub(r"#U([0-9A-Fa-f]{4})", lambda m: chr(int(m.group(1), 16)), name)


def resolve_named_file(folder: Path, base_name: str, suffixes=(".png_", ".png")) -> Path:
    for suffix in suffixes:
        direct = folder / (base_name + suffix)
        if direct.is_file():
            return direct
    for p in folder.iterdir():
        if not p.is_file():
            continue
        decoded = decoded_u_name(p.name)
        for suffix in suffixes:
            if decoded == base_name + suffix:
                return p
    raise FileNotFoundError(f"Resource {base_name!r} not found in {folder}")


def localized_string(raw, texts, lang_key):
    raw = str(raw or "")
    def repl(m):
        idx = int(m.group(1))
        if 0 <= idx < len(texts) and isinstance(texts[idx], dict):
            return str(texts[idx].get(lang_key, ""))
        return ""
    raw = re.sub(r"\\I18N\[(\d+)\]", repl, raw)
    raw = re.sub(r"\\[cC]\[\d+\]", "", raw)
    raw = re.sub(r"\\[iI]\[\d+\]", "", raw)
    raw = raw.replace("\\.", "").replace("\\|", "")
    raw = raw.replace("\\!", "").replace("\\>", "").replace("\\<", "")
    return raw

def make_string_record(values):
    enc = [str(v or "").encode("utf-8") for v in values]
    return struct.pack("<4H", *(len(v) for v in enc)) + b"".join(enc)


def make_item_record(item, texts):
    if not item or not item.get("name"):
        return None
    values = []
    for lk in LANG_KEYS:
        values.append(localized_string(item.get("name", ""), texts, lk).encode("utf-8"))
        values.append(localized_string(item.get("description", ""), texts, lk).encode("utf-8"))
    header = struct.pack("<8H", *(len(v) for v in values))
    return header + b"".join(values)


def write_ui_database(game: Path, out: Path):
    texts = read_json(game / "data" / "I18NTexts.json")
    items = read_json(game / "data" / "Items.json")
    label_count = len(LABEL_SPECS)
    header_size = 20
    item_rec_size = 12
    item_table_off = header_size
    label_table_off = item_table_off + MAX_ITEMS * item_rec_size
    blob_off = label_table_off + label_count * 4
    blob = bytearray()
    item_records = []

    for item_id in range(MAX_ITEMS):
        item = items[item_id] if item_id < len(items) else None
        rec = make_item_record(item, texts)
        if rec is None:
            item_records.append((0, 0, 3, 0, 0))
            continue
        off = len(blob)
        blob += rec
        item_records.append((
            int(item.get("iconIndex", 0)),
            int(item.get("itypeId", 0)),
            int(item.get("occasion", 3)),
            off,
            len(rec),
        ))

    label_offsets = []
    for idx, custom in LABEL_SPECS:
        if custom is not None:
            vals = custom
        else:
            entry = texts[idx] if idx is not None and idx < len(texts) else None
            vals = [str(entry.get(lk, "")) if isinstance(entry, dict) else "" for lk in LANG_KEYS]
        label_offsets.append(len(blob))
        blob += make_string_record(vals)

    raw = bytearray(struct.pack(
        "<4sHHIII", b"NU60", MAX_ITEMS, label_count,
        item_table_off, label_table_off, blob_off
    ))
    for icon, itype, occasion, off, size in item_records:
        raw += struct.pack("<HBBII", icon, itype, occasion, off, size)
    for off in label_offsets:
        raw += struct.pack("<I", off)
    raw += blob
    (out / "ui060.bin").write_bytes(raw)
    return sum(1 for r in item_records if r[4]), label_count


def rgba4444_bytes(img: Image.Image) -> bytes:
    rgba = img.convert("RGBA").tobytes()
    packed = bytearray(len(rgba) // 2)
    j = 0
    for i in range(0, len(rgba), 4):
        r, g, b, a = rgba[i:i+4]
        v = (r >> 4) | ((g >> 4) << 4) | ((b >> 4) << 8) | ((a >> 4) << 12)
        packed[j] = v & 255
        packed[j+1] = (v >> 8) & 255
        j += 2
    return bytes(packed)


def prepare_iconset(game: Path, out: Path, key: bytes):
    src = resolve_named_file(game / "img" / "system", "IconSet")
    img = load_encrypted_png(src, key) if src.suffix == ".png_" else Image.open(src).convert("RGBA")
    if img.size != (512, 512):
        canvas = Image.new("RGBA", (512, 512), (0,0,0,0))
        img.thumbnail((512,512), Image.Resampling.LANCZOS)
        canvas.alpha_composite(img, (0,0))
        img = canvas
    (out / "ui_iconset.rgba4444").write_bytes(rgba4444_bytes(img))


def parse_plugins(game: Path):
    text = (game / "js" / "plugins.js").read_text(encoding="utf-8-sig")
    start = text.find("[")
    end = text.rfind("]")
    if start < 0 or end < start:
        return []
    return json.loads(text[start:end+1])


def title_names(game: Path):
    names = {"en_US": None, "ja_JP": None, "zh_CN": None, "zh_TW": None}
    try:
        for p in parse_plugins(game):
            if p.get("name") != "DisplayI18NTexts" or not p.get("status"):
                continue
            raw = p.get("parameters", {}).get("titleImagesByLanguage", "[]")
            outer = json.loads(raw)
            for ent in outer:
                d = json.loads(ent) if isinstance(ent, str) else ent
                if d.get("language") in names and d.get("imageName1"):
                    names[d["language"]] = d["imageName1"]
    except Exception:
        pass
    system = read_json(game / "data" / "System.json")
    fallback = system.get("title1Name") or "奈落タイトル"
    for k in names:
        if not names[k]: names[k] = fallback
    return names


def prepare_titles(game: Path, out: Path, key: bytes):
    names = title_names(game)
    tags = {"en_US":"en", "ja_JP":"ja", "zh_CN":"zhcn", "zh_TW":"zhtw"}
    cache = {}
    for lk, name in names.items():
        if name not in cache:
            src = resolve_named_file(game / "img" / "titles1", name)
            img = load_encrypted_png(src, key) if src.suffix == ".png_" else Image.open(src).convert("RGBA")
            # Keep the same half-scale geometry used by the PSP world: 816x624
            # -> 408x312, then crop 20 px vertically into the 480x272 viewport.
            scaled = img.resize((max(1, img.width//2), max(1, img.height//2)), Image.Resampling.LANCZOS)
            if scaled.width > 480 or scaled.height > 312:
                scaled.thumbnail((480,312), Image.Resampling.LANCZOS)
            viewport = Image.new("RGBA", (480,272), (0,0,0,255))
            sx = max(0, (scaled.width - 480)//2)
            sy = max(0, (scaled.height - 272)//2)
            crop = scaled.crop((sx, sy, min(sx+480, scaled.width), min(sy+272, scaled.height)))
            viewport.alpha_composite(crop, ((480-crop.width)//2, (272-crop.height)//2))
            tex = Image.new("RGBA", (512,512), (0,0,0,255))
            tex.alpha_composite(viewport, (0,0))
            cache[name] = tex
        (out / f"title_{tags[lk]}.rgba8888").write_bytes(cache[name].tobytes())
    return names



def resolve_audio_file(folder: Path, base_name: str) -> Path:
    return resolve_named_file(folder, base_name, suffixes=(".ogg_", ".ogg", ".m4a_", ".m4a"))


def decrypt_audio_to_pcm(src: Path, key: bytes, dst: Path, volume: float = 1.0, pitch: int = 100):
    if src.suffix.endswith("_"):
        raw = decrypt_mz(src, key)
    else:
        raw = src.read_bytes()
    with tempfile.TemporaryDirectory(prefix="naraku060_") as td:
        inp = Path(td) / "in.ogg"
        inp.write_bytes(raw)
        # RPG Maker's SE pitch changes playback rate.  Bake it into PCM so
        # the PSP audio thread stays intentionally simple.
        rate = max(11025, min(88200, int(round(44100 * float(pitch) / 100.0))))
        filt = f"asetrate={rate},aresample=44100,volume={volume:.6f}"
        cmd = [
            "ffmpeg", "-v", "error", "-y", "-i", str(inp),
            "-af", filt,
            "-f", "s16le", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", str(dst)
        ]
        subprocess.run(cmd, check=True)


def prepare_ui_audio(game: Path, out: Path, key: bytes):
    # Exact UI/title sounds referenced by NARAKU's active Common Events and fixed save points.
    system = read_json(game / "data" / "System.json")
    sounds = system.get("sounds", [])
    def system_sound(index, filename):
        if index >= len(sounds) or not sounds[index].get("name"):
            raise RuntimeError(f"System sound index {index} is missing")
        snd = sounds[index]
        return (game / "audio" / "se", str(snd["name"]), filename, float(snd.get("volume", 90)) / 100.0)

    specs = [
        # Title BGM parameters from System.json: pitch 100, volume 50.
        (game / "audio" / "bgm", "【SE音人】街独特の低音", "bgm_title.pcm", 0.50),
        # MenuCallCommon Common Event 1 explicitly plays this before Scene_Item.
        (game / "audio" / "se", "【魔王魂】-SE1", "se_menu_open.pcm", 0.90),
        # These are explicitly referenced by NARAKU events/Common Events.
        (game / "audio" / "se", "Decision1", "se_decision1.pcm", 0.90),
        (game / "audio" / "se", "Decision2", "se_decision2.pcm", 0.90),
        (game / "audio" / "se", "Cancel2", "se_cancel2.pcm", 0.90),
        (game / "audio" / "se", "Cursor2", "se_cursor2.pcm", 0.90),
        # Stock RPG Maker MZ scenes use System.sounds, not the Decision*/Cursor2
        # files above.  Preserve the game's exact configured sounds.
        system_sound(0, "se_ui_cursor.pcm"),
        system_sound(1, "se_ui_ok.pcm"),
        system_sound(2, "se_ui_cancel.pcm"),
        system_sound(3, "se_ui_buzzer.pcm"),
        system_sound(5, "se_ui_save.pcm"),
        system_sound(6, "se_ui_load.pcm"),

        # Early-story event sounds needed by the real VM pages.  Volumes and
        # pitches match their first/story-critical use in the original game.
        (game / "audio" / "se", "Switch1", "se_switch1.pcm", 0.90, 100),
        (game / "audio" / "se", "Switch2", "se_switch2.pcm", 0.90, 100),
        (game / "audio" / "se", "【魔王魂】モニター", "se_monitor.pcm", 0.60, 150),
        (game / "audio" / "se", "Open9", "se_open9.pcm", 0.15, 60),
        (game / "audio" / "se", "Gate1", "se_gate1.pcm", 0.90, 90),
        (game / "audio" / "se", "Gate2", "se_gate2.pcm", 0.50, 100),
        (game / "audio" / "se", "Sword5", "se_sword5.pcm", 0.75, 70),
        (game / "audio" / "se", "【音々亭】hit_axe3", "se_hit_axe3.pcm", 0.90, 100),
        (game / "audio" / "se", "【音々亭】bonecrush5", "se_bonecrush5.pcm", 0.90, 100),
        (game / "audio" / "se", "Equip2", "se_equip2.pcm", 0.30, 70),
        (game / "audio" / "se", "Slash7", "se_slash7.pcm", 0.90, 130),
        (game / "audio" / "se", "Blow2", "se_blow2.pcm", 0.90, 50),
        (game / "audio" / "se", "Monster5", "se_monster5.pcm", 0.90, 50),
        # Map004 Event 7: grate/hatch opens as Enri climbs up from the ladder.
        (game / "audio" / "se", "【効果音ラボ】石の壁がスライドする", "se_hatch_slide.pcm", 0.90, 150),
    ]
    made = []
    for spec in specs:
        folder, name, filename, volume = spec[:4]
        pitch = int(spec[4]) if len(spec) >= 5 else 100
        src = resolve_audio_file(folder, name)
        dst = out / filename
        decrypt_audio_to_pcm(src, key, dst, volume, pitch)
        made.append(filename)
    return made


def main():
    ap = argparse.ArgumentParser(description="Prepare NARAKU PSP 0.6.0 native UI data")
    ap.add_argument("game", type=Path)
    ap.add_argument("--out", type=Path, default=Path("assets"))
    args = ap.parse_args()
    game = args.game.resolve(); out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    system = read_json(game / "data" / "System.json")
    key_hex = str(system.get("encryptionKey", ""))
    if len(key_hex) != 32:
        raise RuntimeError("System.json encryptionKey is missing or invalid")
    key = bytes.fromhex(key_hex)
    items, labels = write_ui_database(game, out)
    prepare_iconset(game, out, key)
    titles = prepare_titles(game, out, key)
    audio = prepare_ui_audio(game, out, key)
    print("NARAKU PSP 0.6.4 UI prepared")
    print(f"  item records: {items}/{MAX_ITEMS}")
    print(f"  localized UI labels: {labels}")
    print(f"  title images: {titles}")
    print("  iconset: ui_iconset.rgba4444")
    print(f"  UI/title PCM: {len(audio)} files")

if __name__ == "__main__":
    main()
