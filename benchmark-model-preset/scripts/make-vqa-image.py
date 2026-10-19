#!/usr/bin/env python3
"""Build the vision QA probe image: one text token + three shapes.

The token is the hard part — a vision model that reads shapes but mangles
characters (M3.1 Flash read VQA-7319-M3F as V0A-7319-M3F on Oct 19) is not
observer-grade. The observer bar is 4/4 exact: token, shape, color, fill.

Usage: make-vqa-image.py [out.png] [token]
"""

import sys

from PIL import Image, ImageDraw

out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/opencode/vqa.png"
token = sys.argv[2] if len(sys.argv) > 2 else "VQA-7319-M3F"

img = Image.new("RGB", (900, 520), "white")
d = ImageDraw.Draw(img)
d.text((60, 60), token, fill="black")
d.ellipse([700, 60, 820, 180], fill=(220, 30, 30))  # red filled circle
d.rectangle([700, 220, 820, 340], fill=(30, 60, 220))  # blue filled square
d.ellipse([700, 400, 820, 520], outline=(0, 0, 0), width=8)  # black unfilled circle
img.save(out)
print(f"wrote {out} token={token}")
