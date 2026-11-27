"""Annotated storyboard from a rendered Reel + its edit JSON.
    python3 tools/storyboard.py <edit.json> <reel.mp4> <out.jpg> [descriptions.json]
Frames are taken from the actual render (middle of each shot), so crops match the video.
"""
import sys, json, subprocess, tempfile, os
from PIL import Image, ImageDraw, ImageFont

cfg_p, reel, out = sys.argv[1:4]
desc = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
c = json.load(open(cfg_p)); beat = 60 / c["bpm"]
SEC = {"opening": "OPENING", "introduction": "INTRODUCTION", "discovery": "DISCOVERY",
       "transformation": "TRANSFORMATION", "climax": "CLIMAX"}
tmp = tempfile.mkdtemp()

def grab(t, p):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", reel,
                    "-frames:v", "1", "-vf", "scale=300:533", p], check=True)

titles = c.get("titles", [])
t = 0; items = []
for i, s in enumerate(c["shots"]):
    d = s.get("sec", s.get("beats", 0) * beat)
    mid = t + d / 2
    for ti in titles:  # show the title on the shot it sits over
        if t <= ti["start"] < t + d: mid = (ti["start"] + ti["end"]) / 2
    p = os.path.join(tmp, f"{i:02d}.jpg"); grab(mid, p)
    note = s.get("note", "")
    sec = next((v for k, v in SEC.items() if note.lower().startswith(k)), None)
    items.append((i + 1, t, d, s["photo"], isinstance(s.get("in"), dict) and i > 0, p, sec))
    t += d
ed = c["end_card"]["beats"] * beat; p = os.path.join(tmp, "logo.jpg"); grab(t + ed * 0.6, p)
items.append((len(items) + 1, t, ed, "LOGO", True, p, "ENDING"))

F = "brand/fonts/Cormorant.ttf"
fb, fs, fsec = ImageFont.truetype(F, 26), ImageFont.truetype(F, 21), ImageFont.truetype(F, 18)
fh = ImageFont.truetype("brand/fonts/Pinyon.ttf", 64)
cols, tw, th = 5, 300, 533; cw, ch = tw + 30, th + 150; rows = (len(items) + cols - 1) // cols
sheet = Image.new("RGB", (cols * cw + 30, rows * ch + 150), (255, 248, 240)); d = ImageDraw.Draw(sheet)
d.text((30, 30), c.get("title", "Reel") + f" — {c.get('version', '')} storyboard", font=fh, fill=(30, 30, 30))
d.text((32, 112), f"{t + ed:.1f} s · {len(c['shots'])} photos + logo · read left to right, row by row", font=fs, fill=(120, 100, 70))
for k, (n, st, du, ph, dis, p, sec) in enumerate(items):
    x = 30 + (k % cols) * cw; y = 150 + (k // cols) * ch
    sheet.paste(Image.open(p), (x, y))
    if sec:
        w = d.textlength(sec, font=fsec); d.rectangle((x, y, x + w + 16, y + 28), fill=(0, 0, 0))
        d.text((x + 8, y + 4), sec, font=fsec, fill=(232, 215, 174))
    d.text((x, y + th + 8), f"#{n}  ·  {int(st // 60)}:{st % 60:04.1f}  ·  {du:.1f}s", font=fb, fill=(30, 30, 30))
    d.text((x, y + th + 40), (c.get("end_card_label", "Elki Jacobs logo") if ph == "LOGO" else ("Photo " + ph.split("_")[-1].lstrip("0") if ph.split("_")[-1].isdigit() else "Added photo")), font=fb, fill=(160, 120, 60))
    d.text((x, y + th + 74), desc.get(ph, ""), font=fs, fill=(80, 80, 80))
    if dis: d.text((x, y + th + 102), "dissolves in", font=fs, fill=(150, 150, 150))
sheet.save(out, quality=90)
print(out, sheet.size)
