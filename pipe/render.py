"""Render a vertical motivation video from a scene script.

Usage: python3 render.py script.json out.mp4
"""
import json, math, os, re, subprocess, sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from voice import tts
import audio

W, H, FPS = 1080, 1920, 30
FONT = f"{S}/fonts"
F_CAP = ImageFont.truetype(f"{FONT}/montserrat-latin-900-normal.ttf", 76)
F_LABEL = ImageFont.truetype(f"{FONT}/cinzel-latin-900-normal.ttf", 64)
F_STAMP = ImageFont.truetype(f"{FONT}/cinzel-latin-900-normal.ttf", 120)
F_BIG = ImageFont.truetype(f"{FONT}/cinzel-latin-900-normal.ttf", 230)
F_BRAND = ImageFont.truetype(f"{FONT}/cinzel-latin-900-normal.ttf", 96)
F_SMALL = ImageFont.truetype(f"{FONT}/montserrat-latin-800-normal.ttf", 44)
GOLD = (226, 178, 74)
GOLD_L = (250, 214, 130)
RED = (176, 30, 34)
WHITE = (245, 240, 230)
CAP_Y = 1330


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- backgrounds
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
CX, CY = W / 2, 760
THETA = np.arctan2(yy - CY, xx - CX)
RAD = np.sqrt((xx - CX) ** 2 + (yy - CY) ** 2) / math.hypot(W, H)


def veins_texture():
    """Dark stone with faint marble veins, grain and vignette."""
    def noise(scale):
        small = rng.random((H // scale + 2, W // scale + 2)).astype(np.float32)
        return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    n = noise(160) * 0.5 + noise(60) * 0.3 + noise(20) * 0.2
    veins = np.exp(-((np.abs(np.sin(n * 18.0))) ** 0.5) * 6.0)  # thin bright lines
    base = 11 + veins * 16 + rng.normal(0, 3, (H, W))
    vign = 1 - np.clip(RAD * 1.5, 0, 1) ** 2 * 0.85
    lum = base * vign
    rgb = np.stack([lum * 1.05, lum * 0.97, lum * 0.86], -1)
    return np.clip(rgb, 0, 255).astype(np.uint8)


DARK = veins_texture()
GRAIN = [np.clip(rng.normal(0, 4, (H // 2, W // 2)), -12, 12).astype(np.int16) for _ in range(6)]


def sunburst(kind, t):
    if kind == "red":
        c_in, c_out, ray = np.array([150, 40, 32]), np.array([60, 10, 10]), 0.22
    else:
        c_in, c_out, ray = np.array([246, 214, 138]), np.array([168, 118, 46]), 0.18
    r = np.clip(RAD * 1.8, 0, 1)[..., None]
    col = c_in * (1 - r) + c_out * r
    rays = (np.sin(THETA * 14 + t * 0.25) > 0.35).astype(np.float32)
    rays = rays * (1 - np.clip(RAD * 1.6, 0, 1)) * ray
    col = col * (1 + rays[..., None] * (0.9 if kind == "red" else 0.35))
    return np.clip(col, 0, 255).astype(np.uint8)


class Dust:
    def __init__(self, n=70):
        self.p = rng.random((n, 2)) * [W, H]
        self.v = rng.uniform(8, 30, n)
        self.s = rng.uniform(1.5, 4.5, n)
        self.ph = rng.random(n) * 6.28

    def draw(self, d, t, color):
        for (x, y), v, s, ph in zip(self.p, self.v, self.s, self.ph):
            yy_ = (y - v * t) % H
            xx_ = x + 12 * math.sin(t * 0.5 + ph)
            a = int(120 + 120 * math.sin(t * 2 + ph))
            d.ellipse([xx_ - s, yy_ - s, xx_ + s, yy_ + s], fill=color + (max(a, 0),))


DUST = Dust()


# ---------------------------------------------------------------- text helpers
MARK = re.compile(r"(\*[^*]+\*|\^[^^]+\^)")


def parse_marked(text):
    """'Le *seul secret* de' -> [(word, style)], style in plain|gold|red."""
    out = []
    for part in MARK.split(text):
        if not part: continue
        style = "plain"
        if part.startswith("*"): style, part = "gold", part[1:-1]
        elif part.startswith("^"): style, part = "red", part[1:-1]
        out += [(w, style) for w in part.split()]
    return out


def letters(s):
    return re.sub(r"[^a-zà-ÿœæ]", "", s.lower())


def align(tokens, words):
    """Map script tokens to TTS word boundaries by consuming letters in order."""
    stream = []
    for i, w in enumerate(words):
        stream += [(c, i) for c in letters(w["w"])]
    pos, out = 0, []
    for tok in tokens:
        L = letters(tok)
        if not L or pos >= len(stream):
            prev = out[-1] if out else (0.0, 0.1)
            out.append((prev[1], prev[1])); continue
        i0 = stream[pos][1]
        pos = min(pos + len(L), len(stream))
        i1 = stream[pos - 1][1]
        out.append((words[i0]["t0"], words[i1]["t1"]))
    return out


def text_w(font, s):
    b = font.getbbox(s)
    return b[2] - b[0]


def draw_text(img, xy, s, font, fill, shadow=True, stroke=0, anchor="la"):
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((xy[0] + 3, xy[1] + 6), s, font=font, fill=(0, 0, 0, 230), anchor=anchor,
                                stroke_width=stroke + 4, stroke_fill=(0, 0, 0, 230))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke,
                             stroke_fill=(20, 12, 8, 255))


# ---------------------------------------------------------------- assets
_cache = {}


def asset(key):
    if key not in _cache:
        im = Image.open(f"{S}/assets/cut/{key}.png").convert("RGBA")
        if key.split("_")[0] in ("goltz", "atlas", "hercprint", "melen", "hourglass"):
            im = framed(im)
        _cache[key] = im
    return _cache[key]


def framed(im):
    """Engraving card with a thin gold frame and drop shadow."""
    b = 10
    out = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), GOLD + (255,))
    out.paste(im, (b, b))
    pad = 40
    canvas = Image.new("RGBA", (out.width + 2 * pad, out.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("L", canvas.size, 0)
    sh.paste(255, (pad, pad + 14, pad + out.width, pad + out.height + 14))
    canvas.paste((0, 0, 0, 200), (0, 0), sh.filter(ImageFilter.GaussianBlur(18)))
    canvas.alpha_composite(out, (pad, pad))
    return canvas


def fit(im, max_w, max_h):
    r = min(max_w / im.width, max_h / im.height)
    return r


# ---------------------------------------------------------------- scene drawing
def draw_label(img, text, t_in):
    a = ease_out(t_in / 0.35)
    y = 150
    tw = text_w(F_LABEL, text)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    half = (tw / 2 + 40) * a + 0
    for x0, x1 in ((W / 2 - half - 220 * a, W / 2 - half), (W / 2 + half, W / 2 + half + 220 * a)):
        for xs in range(int(x0), int(x1), 22):
            d.line([(xs, y + 40), (min(xs + 12, x1), y + 40)], fill=GOLD + (255,), width=4)
    draw_text(layer, (W / 2, y + 40), text, F_LABEL, GOLD_L + (int(255 * a),), anchor="mm", stroke=1)
    img.alpha_composite(layer)


def draw_stamp(img, text, t_in):
    if t_in < 0: return 0.0
    k = ease_out(t_in / 0.18)
    scale = 2.2 - 1.2 * k
    tw = text_w(F_STAMP, text)
    pw, ph = tw + 90, 190
    st = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rectangle([6, 6, pw - 6, ph - 6], outline=RED + (255,), width=10)
    d.rectangle([22, 22, pw - 22, ph - 22], outline=RED + (255,), width=4)
    d.text((pw / 2, ph / 2 + 4), text, font=F_STAMP, fill=RED + (255,), anchor="mm")
    # ink texture: knock out random speckles
    a = np.asarray(st.getchannel("A"), np.float32)
    speck = np.random.default_rng(len(text)).random(a.shape) > 0.12
    st.putalpha(Image.fromarray((a * speck).astype(np.uint8)))
    st = st.resize((int(pw * scale), int(ph * scale)), Image.BILINEAR).rotate(-9, expand=True, resample=Image.BILINEAR)
    alpha = min(1.0, t_in / 0.08)
    if alpha < 1:
        st.putalpha(st.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(st, (int(W / 2 - st.width / 2), int(1060 - st.height / 2)))
    return max(0.0, 1 - t_in / 0.35)  # shake strength


def draw_big(img, text, t_in, color=GOLD_L):
    k = ease_out(t_in / 0.25)
    scale = 1.35 - 0.35 * k
    font = F_BIG if text_w(F_BIG, text) < 940 else ImageFont.truetype(f"{FONT}/cinzel-latin-900-normal.ttf", int(230 * 900 / text_w(F_BIG, text)))
    layer = Image.new("RGBA", (W, 600), (0, 0, 0, 0))
    draw_text(layer, (W / 2, 300), text, font, color + (255,), anchor="mm", stroke=3)
    layer = layer.resize((int(W * scale), int(600 * scale)), Image.BILINEAR)
    img.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(820 - layer.height / 2)))


def draw_counter(img, spec, t_in, dur):
    a, b = spec
    k = min(1.0, t_in / max(dur * 0.85, 0.1)) ** 2.2
    n = int(a + (b - a) * k)
    draw_text(img, (W / 2, 640), "JOUR", F_LABEL, GOLD_L + (255,), anchor="mm")
    draw_text(img, (W / 2, 860), f"{n}", F_BIG, WHITE + (255,), anchor="mm", stroke=3)


def caption_groups(tokens):
    """Split a scene's tokens into on-screen groups (≤3 words, ≤ ~900px)."""
    groups, cur = [], []
    for i, (w, st, t0, t1) in enumerate(tokens):
        trial = " ".join(x[0] for x in cur + [tokens[i]]).upper()
        if cur and (len(cur) >= 3 or text_w(F_CAP, trial) > 900):
            groups.append(cur); cur = []
        cur.append(tokens[i])
        if re.search(r"[.,!?…:;]$", w):
            groups.append(cur); cur = []
    if cur: groups.append(cur)
    return groups


def draw_caption(img, groups, t):
    g = None
    for grp in groups:
        if t >= grp[0][2] - 0.02: g = grp
    if g is None: return
    if t > g[-1][3] + 0.6 and g is groups[-1]: return
    words = [(w.upper(), st, t0, t1) for w, st, t0, t1 in g]
    space = int(text_w(F_CAP, " ") * 1.7)
    total = sum(text_w(F_CAP, w) for w, *_ in words) + space * (len(words) - 1)
    x = W / 2 - total / 2
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for w, st, t0, t1 in words:
        ww = text_w(F_CAP, w)
        if t >= t0 - 0.02:
            pop = 1 + 0.18 * (1 - ease_out((t - t0) / 0.14))
            col = {"plain": WHITE, "gold": GOLD_L, "red": (232, 58, 52)}[st]
            wl = Image.new("RGBA", (ww + 60, 140), (0, 0, 0, 0))
            draw_text(wl, (30, 30), w, F_CAP, col + (255,), stroke=2)
            if st != "plain":
                ImageDraw.Draw(wl).rectangle([30, 118, 30 + ww, 126], fill=col + (255,))
            if pop > 1.001:
                wl = wl.resize((int(wl.width * pop), int(wl.height * pop)), Image.BILINEAR)
            layer.alpha_composite(wl, (int(x + ww / 2 - wl.width / 2), int(CAP_Y - 30 - (wl.height - 140) / 2)))
        x += ww + space
    img.alpha_composite(layer)


def place_subject(img, sc, t_in, dur):
    im = asset(sc["img"])
    is_print = im.getpixel((im.width // 2, 45))[3] > 200 and sc["img"].split("_")[0] in ("goltz", "atlas", "hercprint", "melen", "hourglass")
    size = sc.get("size", 1.0)
    max_w, max_h = (960, 1050) if is_print else (900, 1080)
    r = fit(im, max_w * size, max_h * size)
    k_in = ease_out(t_in / 0.28)
    z = (1.10 - 0.10 * k_in) * (1 + 0.06 * min(t_in / max(dur, 0.1), 1.2))
    nw, nh = int(im.width * r * z), int(im.height * r * z)
    sub = im.resize((nw, nh), Image.BILINEAR)
    if sc.get("fx") == "blur" and t_in < 0.3:
        sub = sub.filter(ImageFilter.GaussianBlur(18 * (1 - t_in / 0.3)))
    if t_in < 0.12:
        sub.putalpha(sub.getchannel("A").point(lambda v: int(v * t_in / 0.12)))
    cy = sc.get("cy", 770)
    drift = -18 * min(t_in / max(dur, 0.1), 1.2)
    img.alpha_composite(sub, (int(W / 2 - nw / 2), int(cy - nh / 2 + drift)))


def brand_outro(img, t_in, brand):
    k = ease_out(t_in / 0.5)
    draw_text(img, (W / 2, 820), brand, F_BRAND, GOLD_L + (int(255 * k),), anchor="mm", stroke=2)
    d = ImageDraw.Draw(img)
    d.line([(W / 2 - 300 * k, 900), (W / 2 + 300 * k, 900)], fill=GOLD + (255,), width=4)
    draw_text(img, (W / 2, 980), "UN RAPPEL PAR JOUR.", F_SMALL, WHITE + (int(255 * k),), anchor="mm")
    draw_text(img, (W / 2, 1050), "ABONNE-TOI.", F_SMALL, GOLD_L + (int(255 * k),), anchor="mm")


# ---------------------------------------------------------------- build timeline
def build(script, work):
    os.makedirs(work, exist_ok=True)
    scenes = script["scenes"]
    units, cur = [], []
    for i, sc in enumerate(scenes):
        if cur and not sc.get("join"):
            units.append(cur); cur = []
        cur.append(i)
    units.append(cur)
    clips, tcur = [], 0.15
    for u, idxs in enumerate(units):
        text_parts = [parse_marked(scenes[i]["t"]) for i in idxs]
        plain = " ".join(w for part in text_parts for w, _ in part)
        mp3 = f"{work}/u{u:02d}.mp3"
        cache = mp3 + ".json"
        if os.path.exists(cache) and json.load(open(cache))["text"] == plain:
            words = json.load(open(cache))["words"]
        else:
            words = tts(plain, mp3, voice=script.get("voice", "fr-FR-RemyMultilingualNeural"),
                        rate=script.get("rate", "-4%"), pitch=script.get("pitch", "-6Hz"))
            json.dump(dict(text=plain, words=words), open(cache, "w"))
        dur = audio.duration(mp3)
        toks = [(w, st) for part in text_parts for w, st in part]
        times = align([w for w, _ in toks], words)
        k = 0
        for i, part in zip(idxs, text_parts):
            sc = scenes[i]
            sc["_tokens"] = [(w, st, tcur + times[k + j][0], tcur + times[k + j][1]) for j, (w, st) in enumerate(part)]
            sc["_start"] = tcur + (times[k][0] if part else 0) - 0.06
            k += len(part)
        clips.append((mp3, tcur))
        last_end = words[-1]["t1"] if words else dur
        gap = scenes[idxs[-1]].get("pause", 0.22)
        tcur += min(dur, last_end + 0.05) + gap
    scenes[0]["_start"] = 0.0
    for a, b in zip(scenes, scenes[1:]):
        a["_end"] = b["_start"]
    scenes[-1]["_end"] = tcur + 0.2
    total = tcur + 0.2 + script.get("outro", 2.4)
    return scenes, clips, total


def render(script_path, out_path):
    script = json.load(open(script_path))
    work = os.path.splitext(out_path)[0] + "_work"
    scenes, clips, total = build(script, work)
    events = [dict(t=sc["_start"], kind="hit" if sc.get("hit") else "cut") for sc in scenes[1:]]
    events.insert(0, dict(t=0.0, kind="hit"))
    for sc in scenes:
        if sc.get("stamp"): events.append(dict(t=sc["_start"] + 0.2, kind="stamp"))
    outro_t = scenes[-1]["_end"]
    events.append(dict(t=outro_t, kind="hit"))
    wav = f"{work}/mix.wav"
    audio.mix(clips, total, events, wav, seed=script.get("seed", 1))

    n = int(total * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "12M", "-bufsize", "24M",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                           out_path], stdin=subprocess.PIPE)
    groups = {id(sc): caption_groups(sc["_tokens"]) for sc in scenes}
    shake_rng = random.Random(3)
    prev_sc = None
    for f in range(n):
        t = f / FPS
        sc = next((s for s in scenes if s["_start"] <= t < s["_end"]), None)
        bg = "dark" if sc is None else sc.get("bg", "dark")
        if bg == "dark":
            base = DARK
        else:
            base = sunburst(bg, t)
        g = GRAIN[(f // 2) % len(GRAIN)]
        g2 = np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
        frame = Image.fromarray(np.clip(base.astype(np.int16) + g2, 0, 255).astype(np.uint8)).convert("RGBA")
        dl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        DUST.draw(ImageDraw.Draw(dl), t, (255, 222, 150) if bg == "dark" else (255, 245, 220))
        frame.alpha_composite(dl)
        shake = 0.0
        if sc is not None:
            t_in, dur = t - sc["_start"], sc["_end"] - sc["_start"]
            if sc.get("label"): draw_label(frame, sc["label"], t_in)
            if sc.get("img"): place_subject(frame, sc, t_in, dur)
            if sc.get("counter"): draw_counter(frame, sc["counter"], t_in, dur)
            if sc.get("big"): draw_big(frame, sc["big"], t_in, RED if sc.get("big_red") else GOLD_L)
            if sc.get("stamp"): shake = max(shake, draw_stamp(frame, sc["stamp"], t_in - 0.2))
            if sc.get("hit") and t_in < 0.3: shake = max(shake, 0.7 * (1 - t_in / 0.3))
            draw_caption(frame, groups[id(sc)], t)
            if sc.get("hit") and t_in < 0.2:
                fl = Image.new("RGBA", (W, H), (255, 236, 200, int(170 * (1 - t_in / 0.2))))
                frame.alpha_composite(fl)
        else:
            brand_outro(frame, t - outro_t, script.get("brand", "DISCIPLINA"))
        frame = frame.convert("RGB")
        if shake > 0:
            dx, dy = shake_rng.uniform(-1, 1) * 16 * shake, shake_rng.uniform(-1, 1) * 16 * shake
            frame = frame.transform((W, H), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), resample=Image.BILINEAR)
        ff.stdin.write(frame.tobytes())
        if f % 150 == 0: print(f"frame {f}/{n}", flush=True)
    ff.stdin.close(); ff.wait()
    print("done", out_path, f"{total:.1f}s")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
