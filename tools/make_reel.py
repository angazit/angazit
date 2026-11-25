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

def load(name):
    im = Image.open(f"{PH}/{name}.jpg").convert("RGB")
    s = 2600 / max(im.size)
    return im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)

def window(im, cx, cy, z):
    iw, ih = im.size
    if iw / ih > W / H: bh = ih / z; bw = bh * W / H
    else:               bw = iw / z; bh = bw * H / W
    x0 = min(max(cx * iw - bw / 2, 0), iw - bw)
    y0 = min(max(cy * ih - bh / 2, 0), ih - bh)
    return (x0, y0, x0 + bw, y0 + bh)

def render_shot(im, a, b, t):
    e = ease(t)
    return im.resize((W, H), Image.BICUBIC, box=window(im, *[a[i] + (b[i] - a[i]) * e for i in range(3)]))

# logo: key the near-black background to pure black
_l = Image.open(cfg["logo"]).convert("L"); _bg = _l.getpixel((5, 5))
LOGO = _l.point(lambda v: 0 if v <= _bg + 6 else min(255, int((v - _bg) * 255 / (255 - _bg)))).convert("RGB")
def logo_frame(t, dur):
    a = ease(t / 1.0); z = 0.95 + 0.05 * ease(t / dur); side = int(1080 * z)
    fr = Image.new("RGB", (W, H)); fr.paste(LOGO.resize((side, side), Image.LANCZOS), ((W - side) // 2, (H - side) // 2))
    return Image.blend(Image.new("RGB", (W, H)), fr, a)

shots = cfg["shots"]
imgs = {s["photo"]: load(s["photo"]) for s in shots}
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
    "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", str(cfg.get("crf", 18)),
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

for f in range(n):
    ff.stdin.write(frame_at(f / FPS).tobytes())
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
