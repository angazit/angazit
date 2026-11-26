"""Co-branded split end card: two logos, each centred in one half of a 1080x1920 black frame.
    python3 tools/make_end_card.py <top_logo> <bottom_logo> <out.png>
Each logo may be white-on-black or black-on-white (auto-detected and converted to white on black).
"""
import sys
from PIL import Image, ImageOps, ImageDraw

W, H = 1080, 1920
top_p, bot_p, out = sys.argv[1:4]
MAX = {"elki": (560, 560), "default": (680, 360)}  # box each logo fits into, for similar visual weight

def white_on_black(p):
    im = Image.open(p).convert("L")
    bg = im.getpixel((5, 5))
    if bg > 128:  # dark logo on light background -> invert
        im = ImageOps.invert(im); bg = 255 - bg
    im = im.point(lambda v: 0 if v <= bg + 25 else min(255, int((v - bg) * 255 / (255 - bg))))
    return im.crop(im.point(lambda v: 255 if v > 40 else 0).getbbox())

def fit(im, box):
    k = min(box[0] / im.width, box[1] / im.height)
    return im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)

card = Image.new("L", (W, H), 0)
for i, p in enumerate((top_p, bot_p)):
    lg = fit(white_on_black(p), MAX["elki"] if "logo_square" in p else MAX["default"])
    card.paste(lg, ((W - lg.width) // 2, i * H // 2 + (H // 2 - lg.height) // 2))
rgb = Image.merge("RGB", [card] * 3)
ImageDraw.Draw(rgb).line((W // 2 - 90, H // 2, W // 2 + 90, H // 2), fill=(201, 169, 110), width=2)  # gold hairline at the exact midpoint
rgb.save(out)
print(out)
