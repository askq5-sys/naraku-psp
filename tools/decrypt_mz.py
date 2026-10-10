#!/usr/bin/env python3

import json
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"

if len(sys.argv) != 4:
    print("Usage:")
    print("  python3 decrypt_mz.py System.json input.png_ output.png")
    sys.exit(1)

system_path = Path(sys.argv[1])
input_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])

system = json.loads(
    system_path.read_text(encoding="utf-8-sig")
)

key_hex = system.get("encryptionKey", "")

if not key_hex:
    print("ERROR: encryptionKey is empty")
    sys.exit(1)

try:
    key = bytes.fromhex(key_hex)
except ValueError:
    print("ERROR: encryptionKey is not valid hex")
    sys.exit(1)

if len(key) < 16:
    print("ERROR: encryptionKey is too short")
    sys.exit(1)

data = input_path.read_bytes()

if len(data) < 32:
    print("ERROR: encrypted file is too small")
    sys.exit(1)

print("Encryption key :", key_hex)
print("Input size     :", len(data), "bytes")
print("Header         :", data[:16].hex())

# RPG Maker MV/MZ:
# первые 16 байт — служебный заголовок.
# После него первые 16 байт настоящего файла XOR'ятся ключом.
body = bytearray(data[16:])

for i in range(16):
    body[i] ^= key[i]

if body[:8] != PNG_MAGIC:
    print()
    print("ERROR: result is not a PNG")
    print("Result header:", body[:16].hex())
    sys.exit(1)

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_bytes(body)

print()
print("PNG signature  : OK")
print("Output         :", output_path)
print("Output size    :", len(body), "bytes")
