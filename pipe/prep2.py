"""Build the styled asset library ('glacier' look) from library.json."""
import json, os, sys
import numpy as np
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prep import fetch, cutout, fade_bottom, S

ICE = (150, 225, 255)

def cold_marble(rgba):
    rgb, a = rgba.convert("RGB"), rgba.getchannel("A")
    g = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=0.5)
    g = g.point(lambda v: int(255 * (v / 255) ** 1.35))
    g = ImageEnhance.Contrast(g).enhance(1.15).filter(ImageFilter.UnsharpMask(2, 110, 2))
    arr = np.asarray(g, np.float32)[..., None] * np.array((0.9, 0.96, 1.04), np.float32)
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); out.putalpha(a)
    return out

def ice_rim(rgba, glow=26):
    a = rgba.getchannel("A"); pad = glow * 2
    c = Image.new("RGBA", (rgba.width + 2 * pad, rgba.height + 2 * pad), (0, 0, 0, 0))
    big = Image.new("L", c.size, 0); big.paste(a, (pad, pad))
    halo = big.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(glow)).point(lambda v: int(v * 0.5))
    c.paste(Image.new("RGBA", c.size, ICE + (255,)), (0, 0), halo)
    ring = big.filter(ImageFilter.MaxFilter(5))
    c.paste(Image.new("RGBA", c.size, (225, 245, 255, 255)), (0, 0), ring)
    c.alpha_composite(rgba, (pad, pad))
    return c

def ice_sil(rgba, glow=36):
    a = rgba.getchannel("A"); pad = glow * 2
    c = Image.new("RGBA", (rgba.width + 2 * pad, rgba.height + 2 * pad), (0, 0, 0, 0))
    big = Image.new("L", c.size, 0); big.paste(a, (pad, pad))
    c.paste(Image.new("RGBA", c.size, (90, 200, 255, 255)), (0, 0), big.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(glow)))
    c.paste(Image.new("RGBA", c.size, (210, 240, 255, 255)), (0, 0), big.filter(ImageFilter.MaxFilter(5)))
    c.paste(Image.new("RGBA", c.size, (4, 6, 9, 255)), (0, 0), big)
    return c

def cold_print(im):
    g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.1)
    arr = np.asarray(g, np.float32)[..., None] * np.array((0.86, 0.93, 1.0), np.float32)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

if __name__ == "__main__":
    lib = json.load(open(f"{S}/library.json"))
    os.makedirs(f"{S}/assets/lib", exist_ok=True)
    for key, (mode, crop, tags) in lib.items():
        out = f"{S}/assets/lib/{key}.png"
        if os.path.exists(out): continue
        src = key.replace("_sil", "")
        im = fetch(src)
        if crop < 1.0: im = im.crop((0, 0, im.width, int(im.height * crop)))
        if mode == "print":
            res = cold_print(im)
        else:
            c = cutout(im)
            if crop < 1.0: c = fade_bottom(c)
            res = ice_sil(c) if mode == "sil" else ice_rim(cold_marble(c))
        res.save(out); print(key, res.size, flush=True)
