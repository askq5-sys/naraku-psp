#!/usr/bin/env python3
import argparse
import json
import subprocess
import tempfile
from pathlib import Path

# Only SE variants already understood by the v0.5.x runtime.  These are not
# synthetic footsteps: every tuple below comes from an actual RPG Maker event.
SPECS = [
    ("【音々亭】bonecrush4.ogg_", "se_bonecrush4.pcm", 70, 40),
    ("【魔王魂】  水01.ogg_", "se_water.pcm", 100, 90),
    ("【効果音ラボ】水をバシャッとかける1.ogg_", "se_splash.pcm", 50, 20),
    ("【効果音ラボ】水をバシャッとかける1.ogg_", "se_splash_step70.pcm", 70, 5),
    ("【効果音ラボ】水をバシャッとかける1.ogg_", "se_splash_step120.pcm", 120, 5),
    ("【音々亭】bonecrush4.ogg_", "se_bonecrush4_100.pcm", 100, 90),
]

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def decrypt_mz(src: Path, key: bytes) -> bytes:
    data = src.read_bytes()
    if len(data) < 32 or data[:8] != b"RPGMV\x00\x00\x00":
        raise RuntimeError(f"Not encrypted RPG Maker data: {src}")
    out = bytearray(data[16:])
    for i in range(min(16, len(out))):
        out[i] ^= key[i]
    return bytes(out)

def to_pcm(ogg_bytes: bytes, dst: Path, pitch: int, volume: int):
    with tempfile.TemporaryDirectory(prefix="naraku_v051_se_") as td:
        td = Path(td)
        src = td / "in.ogg"
        src.write_bytes(ogg_bytes)
        ratio = pitch / 100.0
        # RPG Maker's pitch changes playback rate.  Bake that rate and event
        # volume into PCM so the PSP runtime can play the exact variant cheaply.
        af = f"asetrate={44100.0 * ratio:.3f},aresample=44100,volume={volume / 100.0:.6f}"
        cmd = [
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
            "-af", af, "-ac", "2", "-ar", "44100", "-f", "s16le", str(dst)
        ]
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError as exc:
            raise RuntimeError("ffmpeg not found: sudo apt install -y ffmpeg") from exc

def main():
    ap = argparse.ArgumentParser(description="Prepare original NARAKU SE variants for PSP v0.5.1")
    ap.add_argument("game")
    ap.add_argument("--out", default="assets")
    args = ap.parse_args()

    game = Path(args.game)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    system = read_json(game / "data" / "System.json")
    key = bytes.fromhex(system.get("encryptionKey", ""))
    if len(key) < 16:
        raise RuntimeError("Invalid encryptionKey")

    se_dir = game / "audio" / "se"
    for src_name, dst_name, pitch, volume in SPECS:
        dst = out / dst_name
        to_pcm(decrypt_mz(se_dir / src_name, key), dst, pitch, volume)
        sec = dst.stat().st_size / (44100 * 2 * 2)
        print(f"{src_name} -> {dst_name}: volume={volume} pitch={pitch} ({sec:.2f}s)")

    print("NARAKU PSP v0.5.1 original-event SE variants ready")

if __name__ == "__main__":
    main()
