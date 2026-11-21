"""Download full-res Met images, cut out statues, stylize (marble + gold outline)."""
import json, os, sys, urllib.request, io
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
meta = json.load(open(f"{S}/data/met_meta.json"))
GOLD = (214, 172, 84)

def fetch(key):
    raw = f"{S}/assets/raw/{key}.jpg"
    if not os.path.exists(raw):
        url = meta[key + ".jpg"]["full"]
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
        im = Image.open(io.BytesIO(data)).convert("RGB")
        im.thumbnail((1800, 1800), Image.LANCZOS)
        im.save(raw, quality=93)
    return Image.open(raw).convert("RGB")

_sess = None
def cutout(im):
    global _sess
    from rembg import remove, new_session
    if _sess is None: _sess = new_session("isnet-general-use")
    out = remove(im, session=_sess, post_process_mask=True)
    bbox = out.getchannel("A").point(lambda a: 255 if a > 40 else 0).getbbox()
    return out.crop(bbox)

def marble(rgba, tint=(1.0, 0.97, 0.9)):
    """Desaturate, raise contrast, warm tint: the 'stone engraving' look."""
    rgb, a = rgba.convert("RGB"), rgba.getchannel("A")
    g = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=0.5)
    g = g.point(lambda v: int(255 * (v / 255) ** 1.45))
    g = ImageEnhance.Contrast(g).enhance(1.12)
    g = g.filter(ImageFilter.UnsharpMask(radius=2, percent=120, threshold=2))
    arr = np.asarray(g, dtype=np.float32)[..., None] * np.array(tint, dtype=np.float32)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    out.putalpha(a)
    return out

def gold_outline(rgba, width=5, glow=18):
    a = rgba.getchannel("A")
    pad = width + glow * 2
    W, H = rgba.size
    canvas = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    big_a = Image.new("L", canvas.size, 0); big_a.paste(a, (pad, pad))
    ring = big_a.filter(ImageFilter.MaxFilter(width * 2 + 1))
    glow_a = ring.filter(ImageFilter.GaussianBlur(glow)).point(lambda v: int(v * 0.55))
    canvas.paste(Image.new("RGBA", canvas.size, GOLD + (255,)), (0, 0), glow_a)
    canvas.paste(Image.new("RGBA", canvas.size, GOLD + (255,)), (0, 0), ring)
    canvas.alpha_composite(rgba, (pad, pad))
    return canvas

def silhouette(rgba, glow=34):
    a = rgba.getchannel("A")
    pad = glow * 2
    W, H = rgba.size
    canvas = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    big_a = Image.new("L", canvas.size, 0); big_a.paste(a, (pad, pad))
    halo = big_a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(glow))
    canvas.paste(Image.new("RGBA", canvas.size, (240, 190, 90, 255)), (0, 0), halo)
    rim = big_a.filter(ImageFilter.MaxFilter(5))
    canvas.paste(Image.new("RGBA", canvas.size, (255, 215, 130, 255)), (0, 0), rim)
    canvas.paste(Image.new("RGBA", canvas.size, (8, 6, 5, 255)), (0, 0), big_a)
    return canvas

def fade_bottom(rgba, frac=0.18):
    """Soft fade at the bottom edge of a cropped cutout."""
    a = np.asarray(rgba.getchannel("A"), dtype=np.float32)
    h = a.shape[0]; n = int(h * frac)
    a[h - n:] *= np.linspace(1, 0, n)[:, None]
    rgba.putalpha(Image.fromarray(a.astype(np.uint8)))
    return rgba

def engraving(im):
    """Prints: sepia-ish monochrome, cropped of museum margins, gold frame."""
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=2)
    arr = np.asarray(g, dtype=np.float32)[..., None] * np.array((1.0, 0.95, 0.85), dtype=np.float32)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
    return out

if __name__ == "__main__":
    os.makedirs(f"{S}/assets/cut", exist_ok=True)
    for spec in sys.argv[1:]:
        key, mode, *rest = spec.split(":")
        crop = float(rest[0]) if rest else 1.0
        out = f"{S}/assets/cut/{key}{'_sil' if mode == 'sil' else ''}.png"
        if os.path.exists(out): continue
        im = fetch(key)
        if crop < 1.0:
            im = im.crop((0, 0, im.width, int(im.height * crop)))
        if mode == "print":
            res = engraving(im)
        else:
            c = cutout(im)
            if crop < 1.0: c = fade_bottom(c)
            res = gold_outline(marble(c)) if mode == "statue" else silhouette(c)
        res.save(out); print(key, res.size, flush=True)
