#!/usr/bin/env python3
import argparse, json, subprocess, tempfile
from pathlib import Path

SPECS = [
    ("Move1.ogg_", "se_step_stone.pcm", 100, 24),
    ("Move2.ogg_", "se_step_soft.pcm", 95, 20),
]

def read_json(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

def decrypt_mz(src: Path, key: bytes) -> bytes:
    data = src.read_bytes()
    if len(data) < 32 or data[:8] != b"RPGMV\x00\x00\x00":
        raise RuntimeError(f"Not encrypted RPG Maker data: {src}")
    out = bytearray(data[16:])
    for i in range(min(16, len(out))):
        out[i] ^= key[i]
    return bytes(out)

def to_pcm(ogg: bytes, dst: Path, pitch: int, volume: int):
    with tempfile.TemporaryDirectory(prefix="naraku_v040_audio_") as td:
        td = Path(td)
        src = td / "in.ogg"
        src.write_bytes(ogg)
        ratio = pitch / 100.0
        # Tiny edge fades remove clicks from short one-shot footstep samples.
        af = (
            f"aresample=44100,asetrate={44100.0*ratio:.3f},aresample=44100,"
            f"volume={volume/100.0:.6f},"
            "atrim=0:0.28,"
            "afade=t=in:st=0:d=0.005,areverse,afade=t=in:st=0:d=0.008,areverse"
        )
        cmd = [
            "ffmpeg","-y","-loglevel","error","-i",str(src),"-af",af,
            "-ac","2","-ar","44100","-f","s16le",str(dst)
        ]
        try:
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            raise RuntimeError("ffmpeg not found: sudo apt install -y ffmpeg")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("game")
    ap.add_argument("--out", default="assets")
    a=ap.parse_args()
    game=Path(a.game); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    sys=read_json(game/"data"/"System.json")
    key=bytes.fromhex(sys.get("encryptionKey", ""))
    if len(key)<16: raise RuntimeError("Invalid encryptionKey")
    for src_name,dst_name,pitch,vol in SPECS:
        src=game/"audio"/"se"/src_name
        dst=out/dst_name
        to_pcm(decrypt_mz(src,key),dst,pitch,vol)
        secs=dst.stat().st_size/(44100*2*2)
        print(f"{src_name} -> {dst_name} ({secs:.2f}s)")
    print("NARAKU PSP v0.4.0 footstep audio ready")
if __name__=="__main__": main()
