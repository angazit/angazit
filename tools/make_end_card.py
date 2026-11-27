"""Co-branded end card: N logos stacked, each centred in an equal band of a 1080x1920 black frame,
with a short gold hairline at each exact boundary.
    python3 tools/make_end_card.py <out.png> <logo1> <logo2> [<logo3> ...]
A logo argument may end in "@x0,y0,x1,y1" to pre-crop the source (e.g. to remove a scan edge).
Black-on-white logos are inverted automatically to white on black.
"""
import sys
from PIL import Image, ImageOps, ImageDraw

W, H = 1080, 1920
out, logos = sys.argv[1], sys.argv[2:]
BAND = H / len(logos)
AREA = 130_000  # px^2 per logo
BOX = {"logo_square": (520, 0.62), "default": (640, 0.46)}  # (max width, max height as share of band)

def white_on_black(arg):
    p, _, crop = arg.partition("@")
    im = Image.open(p).convert("L")
    if crop: im = im.crop(tuple(int(v) for v in crop.split(",")))
    bg = im.getpixel((5, 5))
    if bg > 128: im = ImageOps.invert(im); bg = 255 - bg
    im = im.point(lambda v: 0 if v <= bg + 40 else min(255, int((v - bg) * 255 / (255 - bg))))
    return im.crop(im.point(lambda v: 255 if v > 60 else 0).getbbox())

card = Image.new("L", (W, H), 0)
for i, arg in enumerate(logos):
    # equal visual size: every logo gets the same bounding-box area, capped by width and band height
    lg = white_on_black(arg); mw, mh = BOX["default"]
    k = min((AREA / (lg.width * lg.height)) ** 0.5, mw / lg.width, mh * BAND / lg.height)
    lg = lg.resize((round(lg.width * k), round(lg.height * k)), Image.LANCZOS)
    card.paste(lg, ((W - lg.width) // 2, round(i * BAND + (BAND - lg.height) / 2)))
rgb = Image.merge("RGB", [card] * 3); d = ImageDraw.Draw(rgb)
for i in range(1, len(logos)):
    y = round(i * BAND); d.line((W // 2 - 90, y, W // 2 + 90, y), fill=(201, 169, 110), width=2)
rgb.save(out); print(out)
