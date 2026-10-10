#!/usr/bin/env python3

from PIL import Image
from pathlib import Path
import sys

if len(sys.argv) != 3:
    print("Usage: python3 png_to_psp.py input.png output.rgba")
    sys.exit(1)

src = Path(sys.argv[1])
dst = Path(sys.argv[2])

SCREEN_W = 480
SCREEN_H = 272

TEX_W = 512
TEX_H = 512

img = Image.open(src).convert("RGBA")

print("Original:", img.size)

# Сохраняем пропорции.
img.thumbnail(
    (SCREEN_W, SCREEN_H),
    Image.Resampling.LANCZOS
)

screen = Image.new(
    "RGBA",
    (SCREEN_W, SCREEN_H),
    (0, 0, 0, 255)
)

x = (SCREEN_W - img.width) // 2
y = (SCREEN_H - img.height) // 2

screen.alpha_composite(img, (x, y))

# GE удобнее кормить power-of-two текстурой.
texture = Image.new(
    "RGBA",
    (TEX_W, TEX_H),
    (0, 0, 0, 0)
)

texture.paste(screen, (0, 0))

dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_bytes(texture.tobytes())

# Заодно картинка для проверки глазами.
screen.save(dst.with_suffix(".preview.png"))

print("Visible area :", SCREEN_W, "x", SCREEN_H)
print("Texture      :", TEX_W, "x", TEX_H)
print("RGBA size    :", len(texture.tobytes()), "bytes")
print("Output       :", dst)
