"""TikTok cover (1080x1920) in the 'Glacier' DA.

Usage: python3 cover.py videos/NNN_slug.json out/NNN_slug_couverture.jpg
Script fields used: cover_title ("LE SEUL *SECRET* DE LA FORCE"), cover_img (library key),
cover_label (small top line). Defaults: title, first scene image.
"""
import json, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
W, H = 1080, 1920
ANTON = f"{S}/fonts/anton-latin-400-normal.ttf"
ICE = (110, 222, 255)
WHITE = (240, 246, 250)


def bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - W / 2) ** 2 + (yy - 700) ** 2) / np.hypot(W, H)
    lum = 7 + 60 * np.exp(-(r * 3.0) ** 2)
    lum *= 1 - np.clip(r * 1.4, 0, 1) ** 2 * 0.8
    rng = np.random.default_rng(4)
    lum = lum + rng.normal(0, 2.5, lum.shape)
    return Image.fromarray(np.stack([lum * 0.72, lum * 0.92, lum * 1.25], -1).clip(0, 255).astype(np.uint8)).convert("RGBA")


def asset(key):
    for ext in ("webp", "png"):
        p = f"{S}/assets/lib/{key}.{ext}"
        if os.path.exists(p): return Image.open(p).convert("RGBA")
    raise FileNotFoundError(key)


def wrap(words, font, maxw):
    lines, cur = [], []
    for w in words:
        trial = " ".join(x[0] for x in cur + [w])
        if cur and font.getlength(trial) > maxw:
            lines.append(cur); cur = []
        cur.append(w)
    if cur: lines.append(cur)
    return lines


def make(script, out):
    img = bg()
    key = script.get("cover_img") or next(s["img"] for s in script["scenes"] if s.get("img") and not s["img"].endswith("_sil"))
    sub = asset(key)
    k = min(1000 / sub.width, 1050 / sub.height)
    sub = sub.resize((int(sub.width * k), int(sub.height * k)), Image.LANCZOS)
    img.alpha_composite(sub, (W // 2 - sub.width // 2, 330))
    # dark fade under the title
    fade = Image.new("RGBA", (W, 760), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fade)
    for y in range(760):
        fd.line([(0, y), (W, y)], fill=(4, 6, 10, int(250 * min(1, y / 300))))
    img.alpha_composite(fade, (0, H - 760))
    d = ImageDraw.Draw(img)
    label = script.get("cover_label")
    if label:
        f = ImageFont.truetype(ANTON, 52)
        sp = " ".join(label.upper())
        tw = f.getlength(sp)
        d.text((W / 2, 220), sp, font=f, fill=WHITE, anchor="mm")
        d.line([(W / 2 - tw / 2 - 190, 220), (W / 2 - tw / 2 - 30, 220)], fill=ICE, width=4)
        d.line([(W / 2 + tw / 2 + 30, 220), (W / 2 + tw / 2 + 190, 220)], fill=ICE, width=4)
    title = script.get("cover_title") or script.get("title", "").upper()
    words = []
    for part in re.split(r"(\*[^*]+\*)", title):
        acc = part.startswith("*")
        words += [(w, acc) for w in part.strip("*").split()]
    size = 150
    while True:
        f = ImageFont.truetype(ANTON, size)
        lines = wrap(words, f, 960)
        if len(lines) <= 3 or size <= 96: break
        size -= 8
    lh = int(size * 1.08)
    y0 = 1500 - (len(lines) - 1) * lh / 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    for i, line in enumerate(lines):
        txt = " ".join(w for w, _ in line)
        x = W / 2 - f.getlength(txt) / 2
        for w, acc in line:
            sd.text((x + 3, y0 + i * lh + 8), w, font=f, fill=(0, 0, 0, 255), anchor="lm")
            x += f.getlength(w + " ")
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(8)))
    for i, line in enumerate(lines):
        txt = " ".join(w for w, _ in line)
        x = W / 2 - f.getlength(txt) / 2
        for w, acc in line:
            d.text((x, y0 + i * lh), w, font=f, fill=ICE if acc else WHITE, anchor="lm")
            x += f.getlength(w + " ")
    hf = ImageFont.truetype(f"{S}/fonts/montserrat-latin-800-normal.ttf", 38)
    d.text((W / 2, 1800), "@cotidie.mentalite", font=hf, fill=(160, 180, 195), anchor="mm")
    img.convert("RGB").save(out, quality=94)


if __name__ == "__main__":
    make(json.load(open(sys.argv[1])), sys.argv[2])
    print(sys.argv[2])
