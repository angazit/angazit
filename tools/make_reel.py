"""Elki Jacobs Design - photo Reel renderer (config driven).

    python3 tools/make_reel.py <edit.json> <photos_dir> <out.mp4> [--storyboard out.jpg]

edit.json holds the whole timeline, so a revision = edit the JSON and re-render.
Shot fields:
  photo        file name (without .jpg) in photos_dir
  beats        duration in beats of the timeline BPM (or "sec")
  from / to    camera [cx, cy, zoom]: centre (0-1 of the photo) and zoom
               (1.0 = largest 9:16 window that fits; >1 = tighter). Omit "to" = static.
  in           "cut" (default) or {"dissolve": seconds}
Originals are never modified; colour is left as the photographer delivered it.
"""
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont

cfg_path, PH, OUT = sys.argv[1:4]
SB = sys.argv[sys.argv.index("--storyboard") + 1] if "--storyboard" in sys.argv else None
cfg = json.load(open(cfg_path))
W, H, FPS = 1080, 1920, cfg.get("fps", 30)
BEAT = 60 / cfg["bpm"]
ease = lambda t: 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, t)))

from functools import lru_cache
@lru_cache(maxsize=3)  # full-resolution originals; only the current/previous shots stay in memory
def load(name):
    return Image.open(f"{PH}/{name}.jpg").convert("RGB")

def window(im, cx, cy, z):
    iw, ih = im.size
    if iw / ih > W / H: bh = ih / z; bw = bh * W / H
    else:               bw = iw / z; bh = bw * H / W
    x0 = min(max(cx * iw - bw / 2, 0), iw - bw)
    y0 = min(max(cy * ih - bh / 2, 0), ih - bh)
    return (x0, y0, x0 + bw, y0 + bh)

def render_shot(im, a, b, t):
    e = ease(t)
    return im.resize((W, H), Image.LANCZOS, box=window(im, *[a[i] + (b[i] - a[i]) * e for i in range(3)]), reducing_gap=3.0)

# logo: key the near-black background to pure black
_l = Image.open(cfg["logo"]).convert("L"); _bg = _l.getpixel((5, 5))
LOGO = _l.point(lambda v: 0 if v <= _bg + 6 else min(255, int((v - _bg) * 255 / (255 - _bg)))).convert("RGB")
CARD = Image.open(cfg["end_card"]["image"]).convert("RGB") if "image" in cfg["end_card"] else None
def logo_frame(t, dur):
    a = ease(t / 1.0); z = 0.95 + 0.05 * ease(t / dur); fr = Image.new("RGB", (W, H))
    if CARD:  # full-frame end card (e.g. co-branded split), slow 5% scale from centre
        cw, ch = int(W * z), int(H * z); fr.paste(CARD.resize((cw, ch), Image.LANCZOS), ((W - cw) // 2, (H - ch) // 2))
    else:
        side = int(1080 * z); fr.paste(LOGO.resize((side, side), Image.LANCZOS), ((W - side) // 2, (H - side) // 2))
    return Image.blend(Image.new("RGB", (W, H)), fr, a)

shots = cfg["shots"]
class _Imgs(dict):
    def __getitem__(self, k): return load(k)
imgs = _Imgs()
starts, t = [], 0.0
for i, s in enumerate(shots):
    s["dur"] = s.get("sec", s.get("beats", 0) * BEAT)
    s["to"] = s.get("to", s["from"])
    x = s.get("in", "cut"); s["xf"] = x["dissolve"] if isinstance(x, dict) else 0.0
    starts.append(t); t += s["dur"]
end = cfg["end_card"]; end_x = end.get("dissolve", 0.6); end_dur = end["beats"] * BEAT
logo_start = t; total = t + end_dur
n = round(total * FPS)

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
    "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(cfg.get("crf", 14)), "-tune", "film", "-x264-params", "aq-mode=3",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)

def frame_at(tt):
    # current shot = last shot whose start <= tt; a dissolve blends the previous shot over its first xf seconds
    i = max(k for k in range(len(shots)) if starts[k] <= tt) if tt < logo_start else None
    if i is None:
        lt = tt - logo_start
        lf = logo_frame(lt, end_dur)
        if lt < end_x:
            last = shots[-1]
            prev = render_shot(imgs[last["photo"]], last["from"], last["to"], 1.0)
            return Image.blend(prev, lf, ease(lt / end_x))
        return lf
    s = shots[i]; lt = tt - starts[i]
    fr = render_shot(imgs[s["photo"]], s["from"], s["to"], lt / s["dur"])
    if i and s["xf"] and lt < s["xf"]:
        p = shots[i - 1]
        pf = render_shot(imgs[p["photo"]], p["from"], p["to"], 1.0)  # previous shot holds its last position
        fr = Image.blend(pf, fr, ease(lt / s["xf"]))
    return fr

# optional title: {"script": "...", "caps": "...", "start": s, "end": s, "y": px}
from PIL import ImageFilter
IVORY, GOLD = (255, 248, 240), (232, 215, 174)
FD = cfg.get("fonts", "brand/fonts")
def title_layer(ti, alpha):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); a = int(255 * alpha)
    f1 = ImageFont.truetype(f"{FD}/Pinyon.ttf", ti.get("script_size", 150))
    f2 = ImageFont.truetype(f"{FD}/Cormorant.ttf", ti.get("caps_size", 34)); sp = 9
    y = ti.get("y", 760)
    d.text(((W - d.textlength(ti["script"], font=f1)) / 2, y), ti["script"], font=f1, fill=IVORY + (a,))
    cw = sum(d.textlength(c, font=f2) for c in ti["caps"]) + sp * (len(ti["caps"]) - 1); x = (W - cw) / 2
    for c in ti["caps"]:
        d.text((x, y + 205), c, font=f2, fill=GOLD + (a,)); x += d.textlength(c, font=f2) + sp
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda v: v * 0.75))
    return Image.alpha_composite(sh, lay)

for f in range(n):
    tt = f / FPS; fr = frame_at(tt)
    for ti in cfg.get("titles", []):
        st, en = ti["start"], ti["end"]
        a = min(ease((tt - st) / 0.5), 1 - ease((tt - (en - 0.4)) / 0.4)) if st <= tt < en else 0
        if a > 0: fr = Image.alpha_composite(fr.convert("RGBA"), title_layer(ti, a)).convert("RGB")
    ff.stdin.write(fr.tobytes())
ff.stdin.close(); ff.wait()

print(f"{OUT}: {total:.1f}s @ {cfg['bpm']} BPM ({total / BEAT:.0f} beats), {len(shots)} shots")
for s, st in zip(shots, starts):
    print(f"  {st:5.2f}s  {s['photo']:7s} {s['dur']:.2f}s  {'dissolve' if s['xf'] else 'cut'}  {s.get('note', '')}")
print(f"  {logo_start:5.2f}s  LOGO    {end_dur:.2f}s")

if SB:  # storyboard: first frame of every shot with timestamp
    th = []
    for s, st in zip(shots, starts):
        im = render_shot(imgs[s["photo"]], s["from"], s["to"], 0.5).resize((216, 384))
        d = ImageDraw.Draw(im); d.rectangle((0, 350, 216, 384), fill=(0, 0, 0))
        d.text((6, 356), f"{st:4.1f}s  {s['photo']}  {s['dur']:.1f}s", fill=(255, 255, 255))
        th.append(im)
    th.append(logo_frame(2, end_dur).resize((216, 384)))
    cols = 8; rows = math.ceil(len(th) / cols)
    sheet = Image.new("RGB", (cols * 222 + 6, rows * 390 + 6), "white")
    for k, im in enumerate(th): sheet.paste(im, (6 + (k % cols) * 222, 6 + (k // cols) * 390))
    sheet.save(SB, quality=90)
