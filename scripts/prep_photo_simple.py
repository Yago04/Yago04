"""
Prepare a portrait photo for clean ASCII conversion using only Pillow + numpy.
No rembg or opencv needed — uses contrast enhancement and smart thresholding
to isolate the subject on a white background.

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.

    python scripts/prep_photo_simple.py <input.png> [output.png]
"""
import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")

img = Image.open(INP).convert("RGBA")

# If the image has an alpha channel, use it to composite on white
r, g, b, a = img.split()
bg = Image.new("RGB", img.size, (255, 255, 255))
fg = Image.merge("RGB", (r, g, b))
bg.paste(fg, mask=a)
gray = bg.convert("L")

# Boost local contrast using unsharp mask
gray = gray.filter(ImageFilter.UnsharpMask(radius=3, percent=180, threshold=3))

# Global contrast + brightness tuning
gray = ImageEnhance.Contrast(gray).enhance(1.6)
gray = ImageEnhance.Brightness(gray).enhance(1.15)

# Auto-levels: stretch histogram to use the full range
arr = np.array(gray, dtype=np.float32)
lo, hi = np.percentile(arr, 2), np.percentile(arr, 98)
arr = np.clip((arr - lo) / max(hi - lo, 1) * 255, 0, 255).astype(np.uint8)
gray = Image.fromarray(arr, mode="L")

gray.save(OUT)
print("wrote", OUT, gray.size)
