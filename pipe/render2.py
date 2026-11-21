"""DA 'Glacier' renderer: fast cuts, cold marble, ice-blue accents.

Usage: python3 render2.py script.json out.mp4
"""
import json, math, os, re, subprocess, sys, random
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
S = os.path.dirname(HERE)
sys.path.insert(0, HERE)

W, H, FPS = 1080, 1920, 30
FONTS = f"{S}/fonts"
ANTON = f"{FONTS}/anton-latin-400-normal.ttf"
F_CAP = ImageFont.truetype(ANTON, 104)
F_LABEL = ImageFont.truetype(ANTON, 54)
F_TAG = ImageFont.truetype(ANTON, 110)
F_BIG = ImageFont.truetype(ANTON, 300)
F_BRAND = ImageFont.truetype(ANTON, 150)
F_SMALL = ImageFont.truetype(f"{FONTS}/montserrat-latin-800-normal.ttf", 42)
ICE = (110, 222, 255)
ICE_D = (10, 92, 214)
WHITE = (240, 246, 250)
INK = (8, 10, 14)
CAP_Y = 1300
HANDLE = "@cotidie.mentalite"
LIB = json.load(open(f"{S}/library.json"))
PRINT_KEYS = {k for k, v in LIB.items() if v[0] == "print"}


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


# ---------------------------------------------------------------- backgrounds
def _noise(rng, scale):
    small = rng.random((H // scale + 2, W // scale + 2)).astype(np.float32)
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255


def make_bgs():
    rng = np.random.default_rng(11)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rad = np.sqrt((xx - W / 2) ** 2 + (yy - 780) ** 2) / math.hypot(W, H)
    fog = _noise(rng, 220) * 0.6 + _noise(rng, 80) * 0.4
    vign = 1 - np.clip(rad * 1.5, 0, 1) ** 2 * 0.9
    lum = (6 + fog * 22 + 28 * np.exp(-(rad * 3.2) ** 2)) * vign
    dark = np.stack([lum * 0.75, lum * 0.92, lum * 1.15], -1)
    n = _noise(rng, 140) * 0.5 + _noise(rng, 40) * 0.3 + _noise(rng, 14) * 0.2
    veins = np.exp(-(np.abs(np.sin(n * 16.0)) ** 0.5) * 5.0)
    marble = 222 - veins * 55 - _noise(rng, 30) * 10
    marble *= 1 - np.clip(rad * 1.4, 0, 1) ** 2 * 0.35
    light = np.stack([marble * 0.97, marble * 0.99, marble * 1.02], -1)
    deep = np.clip(1 - rad * 1.7, 0, 1)
    blue = np.stack([4 + 10 * deep, 12 + 50 * deep, 30 + 120 * deep], -1)
    f = lambda a: np.clip(a, 0, 255).astype(np.uint8)
    return {"dark": f(dark), "light": f(light), "blue": f(blue)}


class Streaks:
    """Warp-speed lines for the 'blue' punch background."""
    def __init__(self, n=140):
        r = random.Random(5)
        self.s = [(r.uniform(0, 6.283), r.uniform(0, 1), r.uniform(0.6, 1.6), r.uniform(1.5, 4)) for _ in range(n)]

    def draw(self, d, t):
        cx, cy = W / 2, 780
        for ang, ph, sp, wdt in self.s:
            k = (ph + t * sp * 0.9) % 1.0
            r0 = 80 + k ** 2 * 1500
            r1 = r0 + 60 + k * 420
            a = int(220 * min(1, k * 3))
            d.line([(cx + math.cos(ang) * r0, cy + math.sin(ang) * r0),
                    (cx + math.cos(ang) * r1, cy + math.sin(ang) * r1)], fill=(160, 230, 255, a), width=int(wdt))


class Dust:
    def __init__(self, n=55):
        r = np.random.default_rng(3)
        self.p = r.random((n, 2)) * [W, H]; self.v = r.uniform(10, 40, n)
        self.s = r.uniform(1.2, 3.6, n); self.ph = r.random(n) * 6.28

    def draw(self, d, t, col):
        for (x, y), v, s, ph in zip(self.p, self.v, self.s, self.ph):
            yy_ = (y - v * t) % H; xx_ = x + 14 * math.sin(t * 0.6 + ph)
            a = int(110 + 110 * math.sin(t * 2.2 + ph))
            d.ellipse([xx_ - s, yy_ - s, xx_ + s, yy_ + s], fill=col + (max(a, 0),))


# ---------------------------------------------------------------- text / timing
MARK = re.compile(r"(\*[^*]+\*|\^[^^]+\^)")


def parse_marked(text):
    out = []
    for part in MARK.split(text):
        if not part: continue
        st = "plain"
        if part.startswith("*"): st, part = "accent", part[1:-1]
        elif part.startswith("^"): st, part = "block", part[1:-1]
        out += [(w, st) for w in part.split()]
    return out


def letters(s):
    return re.sub(r"[^a-zà-ÿœæ]", "", s.lower())


def align(tokens, words):
    stream = []
    for i, w in enumerate(words):
        stream += [(c, i) for c in letters(w["w"])]
    pos, out = 0, []
    for tok in tokens:
        L = letters(tok)
        if not L or pos >= len(stream):
            prev = out[-1] if out else (0.0, 0.1)
            out.append((prev[1], prev[1])); continue
        i0 = stream[pos][1]; pos = min(pos + len(L), len(stream)); i1 = stream[pos - 1][1]
        out.append((words[i0]["t0"], words[i1]["t1"]))
    return out


def tw(font, s):
    b = font.getbbox(s); return b[2] - b[0]


def text_sh(img, xy, s, font, fill, anchor="la", blur=7, sh=(0, 0, 0, 235), stroke=0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text((xy[0] + 2, xy[1] + 7), s, font=font, fill=sh, anchor=anchor, stroke_width=stroke + 5, stroke_fill=sh)
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, s, font=font, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=INK + (255,))


# ---------------------------------------------------------------- timeline
def _rate(script, u):
    """Base rate +10% with a small per-sentence variation, like a real speaker."""
    base = int(str(script.get("rate", "+10%")).rstrip("%"))
    v = base + random.Random(u * 7 + 1).choice([-3, -1, 0, 2, 4])
    return f"{v:+d}%"


def build(script, work):
    from voice import tts
    from audio import duration
    os.makedirs(work, exist_ok=True)
    scenes = script["scenes"]
    units, cur = [], []
    for i, sc in enumerate(scenes):
        if cur and not sc.get("join"): units.append(cur); cur = []
        cur.append(i)
    units.append(cur)
    clips, tcur = [], 0.1
    for u, idxs in enumerate(units):
        parts = [parse_marked(scenes[i]["t"]) for i in idxs]
        plain = " ".join(w for p in parts for w, _ in p)
        mp3 = f"{work}/u{u:02d}.mp3"; cache = mp3 + ".json"
        if os.path.exists(cache) and json.load(open(cache))["text"] == plain:
            words = json.load(open(cache))["words"]
        else:
            words = tts(plain, mp3, voice=script.get("voice", "fr-FR-RemyMultilingualNeural"),
                        rate=_rate(script, u), pitch=script.get("pitch", "+0Hz"))
            json.dump(dict(text=plain, words=words), open(cache, "w"))
        dur = duration(mp3)
        toks = [w for p in parts for w, _ in p]
        times = align(toks, words)
        k = 0
        for i, p in zip(idxs, parts):
            sc = scenes[i]
            sc["_tokens"] = [(w, st, tcur + times[k + j][0], tcur + times[k + j][1]) for j, (w, st) in enumerate(p)]
            sc["_start"] = tcur + (times[k][0] if p else 0) - 0.05
            k += len(p)
        clips.append((mp3, tcur))
        last_end = words[-1]["t1"] if words else dur
        tcur += min(dur, last_end + 0.04) + min(scenes[idxs[-1]].get("pause", 0.06), script.get("max_pause", 0.12))
    scenes[0]["_start"] = 0.0
    for a, b in zip(scenes, scenes[1:]): a["_end"] = b["_start"]
    scenes[-1]["_end"] = tcur + 0.15
    return scenes, clips, tcur + 0.15 + script.get("outro", 2.2)


def plan_shots(scenes, seed, shot_len=0.72, grid=None):
    """Split every image scene into fast sub-shots cut on word starts."""
    rng = random.Random(seed)
    recent = []
    moves = ["push", "pull", "panL", "panR", "rise"]
    for sc in scenes:
        sc["_shots"] = []
        if not sc.get("img") and not sc.get("tags"):
            continue
        dur = sc["_end"] - sc["_start"]
        n = max(1, min(int(round(dur / shot_len)), 10)) if not sc.get("hold") else 1
        starts = [w[2] for w in sc["_tokens"][1:]]
        cuts = [sc["_start"]]
        for k in range(1, n):
            target = sc["_start"] + dur * k / n
            pool_t = grid if grid is not None else starts
            pool_t = [g for g in pool_t if sc["_start"] < g < sc["_end"]] if pool_t is not None else []
            c = min(pool_t, key=lambda s: abs(s - target)) if pool_t else target
            if c - cuts[-1] > shot_len * 0.6 and sc["_end"] - c > shot_len * 0.45: cuts.append(c)
        primary = sc.get("img")
        tags = set(sc.get("tags") or (LIB[primary][2] if primary in LIB else []))
        pool = [k for k, v in LIB.items() if tags & set(v[2]) and k != primary and not k.endswith("_sil")]
        for j, c in enumerate(cuts):
            if j == 0 and primary:
                key = primary
            else:
                cand = [k for k in pool if k not in recent] or pool or [primary]
                key = rng.choice(cand)
            recent = (recent + [key])[-8:]
            sc["_shots"].append(dict(t=c, key=key, move=rng.choice(moves), seed=rng.random()))
    return scenes


# ---------------------------------------------------------------- drawing
_assets = {}


def asset(key):
    if key not in _assets:
        im = Image.open(f"{S}/assets/lib/{key}.webp" if os.path.exists(f"{S}/assets/lib/{key}.webp") else f"{S}/assets/lib/{key}.png").convert("RGBA")
        if key in PRINT_KEYS:
            b = 6
            fr = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), (225, 240, 250, 255)); fr.paste(im, (b, b))
            pad = 40
            c = Image.new("RGBA", (fr.width + 2 * pad, fr.height + 2 * pad), (0, 0, 0, 0))
            sh = Image.new("L", c.size, 0); sh.paste(255, (pad, pad + 16, pad + fr.width, pad + fr.height + 16))
            c.paste((0, 0, 0, 210), (0, 0), sh.filter(ImageFilter.GaussianBlur(20)))
            c.alpha_composite(fr, (pad, pad)); im = c
        _assets[key] = im
    return _assets[key]


def draw_shot(img, sc, shot, t, t_end, kw_punch):
    im = asset(shot["key"])
    is_print = shot["key"] in PRINT_KEYS
    size = sc.get("size", 1.0) if shot["key"] == sc.get("img") else 1.0
    mw, mh = (1000, 1100) if is_print else (980, 1120)
    r = min(mw * size / im.width, mh * size / im.height)
    ti = t - shot["t"]; d = max(t_end - shot["t"], 0.2); k = min(ti / d, 1.0)
    mv = shot["move"]
    z = {"push": 1.0 + 0.16 * k, "pull": 1.16 - 0.14 * k}.get(mv, 1.08)
    z *= 1 + 0.28 * (1 - ease_out(ti / 0.16))  # entry punch
    z *= kw_punch
    dx = {"panL": 70 - 140 * k, "panR": -70 + 140 * k}.get(mv, 0)
    dy = -50 * k if mv == "rise" else -15 * k
    nw, nh = max(2, int(im.width * r * z)), max(2, int(im.height * r * z))
    sub = im.resize((nw, nh), Image.BILINEAR)
    if ti < 0.07:  # whip smear on entry
        sm = sub.resize((max(2, nw // 10), nh), Image.BILINEAR).resize((nw, nh), Image.BILINEAR)
        sub = Image.blend(sub, sm, 0.7)
    if sc.get("fx") == "blur" and ti < 0.3 and shot is sc["_shots"][0]:
        sub = sub.filter(ImageFilter.GaussianBlur(16 * (1 - ti / 0.3)))
    cy = sc.get("cy", 790)
    img.alpha_composite(sub, (int(W / 2 - nw / 2 + dx), int(cy - nh / 2 + dy)))


def draw_label(img, text, ti, light):
    a = ease_out(ti / 0.25)
    col = (INK if light else WHITE) + (int(255 * a),)
    spaced = " ".join(text)
    w = tw(F_LABEL, spaced)
    d = ImageDraw.Draw(img)
    L = 160 * a
    d.line([(W / 2 - w / 2 - 30 - L, 182), (W / 2 - w / 2 - 30, 182)], fill=ICE + (255,), width=4)
    d.line([(W / 2 + w / 2 + 30, 182), (W / 2 + w / 2 + 30 + L, 182)], fill=ICE + (255,), width=4)
    text_sh(img, (W / 2, 182), spaced, F_LABEL, col, anchor="mm", blur=5, sh=(0, 0, 0, 0 if light else 200))


def draw_tag(img, text, ti):
    """White tape strip with black text, slams in from the left."""
    if ti < 0: return 0.0
    k = ease_out(ti / 0.14)
    w = tw(F_TAG, text) + 80
    strip = Image.new("RGBA", (w, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(strip)
    d.rectangle([0, 10, w, 160], fill=(244, 248, 252, 255))
    d.rectangle([0, 10, 14, 160], fill=ICE + (255,))
    d.text((w / 2 + 6, 86), text, font=F_TAG, fill=INK + (255,), anchor="mm")
    strip = strip.rotate(5, expand=True, resample=Image.BILINEAR)
    x = int(-strip.width + (W / 2 + strip.width / 2) * k)
    img.alpha_composite(strip, (x, 1040 - strip.height // 2))
    return max(0.0, 1 - ti / 0.3) if ti > 0.12 else 0.0


def draw_big(img, text, ti, light):
    k = ease_out(ti / 0.2)
    sc = 1.5 - 0.5 * k
    font = F_BIG if tw(F_BIG, text) < 960 else ImageFont.truetype(ANTON, int(300 * 960 / tw(F_BIG, text)))
    layer = Image.new("RGBA", (W, 520), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    off = int(14 * (1 - k)) + 6
    d.text((W / 2 - off, 260), text, font=font, fill=ICE + (200,), anchor="mm")
    d.text((W / 2 + off, 260), text, font=font, fill=(ICE_D if light else (40, 60, 255)) + (160,), anchor="mm")
    d.text((W / 2, 260), text, font=font, fill=(INK if light else WHITE) + (255,), anchor="mm")
    layer = layer.resize((int(W * sc), int(520 * sc)), Image.BILINEAR)
    img.alpha_composite(layer, (int(W / 2 - layer.width / 2), int(800 - layer.height / 2)))


def draw_counter(img, spec, ti, dur, light):
    a, b = spec
    k = min(1.0, ti / max(dur * 0.85, 0.1)) ** 2.2
    col = (INK if light else WHITE) + (255,)
    text_sh(img, (W / 2, 600), "J O U R", F_LABEL, ICE + (255,), anchor="mm")
    text_sh(img, (W / 2, 830), f"{int(a + (b - a) * k)}", F_BIG, col, anchor="mm")


def caption_groups(tokens):
    groups, cur = [], []
    for tok in tokens:
        trial = " ".join(x[0] for x in cur + [tok]).upper()
        if cur and (len(cur) >= 3 or tw(F_CAP, trial) > 920):
            groups.append(cur); cur = []
        cur.append(tok)
        if re.search(r"[.,!?…:;]$", tok[0]): groups.append(cur); cur = []
    if cur: groups.append(cur)
    return groups


def draw_caption(img, groups, t, light):
    g = None
    for grp in groups:
        if t >= grp[0][2] - 0.02: g = grp
    if g is None: return
    words = [(w.upper(), st, t0) for w, st, t0, _ in g]
    sp = int(tw(F_CAP, " ") * 1.9)
    widths = [tw(F_CAP, w) + (36 if st == "block" else 0) for w, st, _ in words]
    x = W / 2 - (sum(widths) + sp * (len(words) - 1)) / 2
    for (w, st, t0), ww in zip(words, widths):
        if t >= t0 - 0.02:
            pop = 1 + 0.14 * (1 - ease_out((t - t0) / 0.1))
            wl = Image.new("RGBA", (ww + 80, 190), (0, 0, 0, 0))
            if st == "block":
                ImageDraw.Draw(wl).rectangle([40, 30, 40 + ww, 165], fill=(WHITE if not light else INK) + (255,))
                ImageDraw.Draw(wl).text((40 + ww / 2, 98), w, font=F_CAP, fill=(INK if not light else WHITE) + (255,), anchor="mm")
            else:
                col = {"plain": INK if light else WHITE, "accent": ICE_D if light else ICE}[st]
                text_sh(wl, (40, 40), w, F_CAP, col + (255,), sh=(0, 0, 0, 90 if light else 240), stroke=0 if light else 1)
            if pop > 1.001:
                wl = wl.resize((int(wl.width * pop), int(wl.height * pop)), Image.BILINEAR)
            img.alpha_composite(wl, (int(x + ww / 2 - wl.width / 2), int(CAP_Y - 40 - (wl.height - 190) / 2)))
        x += ww + sp


def outro(img, ti, brand):
    k = ease_out(ti / 0.4)
    text_sh(img, (W / 2, 800), brand, F_BRAND, WHITE + (int(255 * k),), anchor="mm")
    ImageDraw.Draw(img).rectangle([W / 2 - 280 * k, 905, W / 2 + 280 * k, 911], fill=ICE + (255,))
    text_sh(img, (W / 2, 975), "UN RAPPEL PAR JOUR.", F_SMALL, WHITE + (int(255 * k),), anchor="mm", blur=4)
    text_sh(img, (W / 2, 1040), "ABONNEZ-VOUS.", F_SMALL, ICE + (int(255 * k),), anchor="mm", blur=4)
    text_sh(img, (W / 2, 1150), HANDLE, F_SMALL, (170, 190, 205, int(230 * k)), anchor="mm", blur=4)


def chroma(frame, amt):
    a = np.asarray(frame)
    o = int(amt)
    out = a.copy()
    out[:, o:, 0] = a[:, :-o, 0]
    out[:, :-o, 2] = a[:, o:, 2]
    return Image.fromarray(out)


# ---------------------------------------------------------------- frame worker
G = {}


def init_worker(state):
    G.update(state)
    G["bgs"] = make_bgs()
    G["streaks"] = Streaks(); G["dust"] = Dust()
    rng = np.random.default_rng(2)
    G["grain"] = [np.clip(rng.normal(0, 4, (H // 2, W // 2)), -12, 12).astype(np.int16) for _ in range(4)]


def render_range(args):
    f0, f1, path = args
    scenes, total, outro_t, kw, brand = G["scenes"], G["total"], G["outro_t"], G["kw"], G["brand"]
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-maxrate", "9M", "-bufsize", "18M",
                           "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    srng = random.Random(f0)
    for f in range(f0, f1):
        t = f / FPS
        sc = next((s for s in scenes if s["_start"] <= t < s["_end"]), None)
        bg = sc.get("bg", "dark") if sc else "dark"
        light = bg == "light"
        g = G["grain"][(f // 2) % 4]
        base = G["bgs"][bg].astype(np.int16) + np.repeat(np.repeat(g, 2, 0), 2, 1)[..., None]
        frame = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        if bg == "blue": G["streaks"].draw(d, t)
        elif not light: G["dust"].draw(d, t, (190, 230, 255))
        frame.alpha_composite(ov)
        shake, ab = 0.0, 0.0
        if sc:
            ti, dur = t - sc["_start"], sc["_end"] - sc["_start"]
            punch = 1.0
            for kt in kw:
                if 0 <= t - kt < 0.15: punch = 1 + 0.06 * (1 - (t - kt) / 0.15)
            if t >= (0 if G.get("music") else G["drop_t"]):
                import bisect
                bl = G["beats"]; j = bisect.bisect_right(bl, t) - 1
                ph = t - bl[j] if j >= 0 else 1.0
                if ph < 0.09: punch *= 1 + 0.035 * (1 - ph / 0.09)
            shots = sc["_shots"]
            cur = [s for s in shots if s["t"] <= t]
            if cur:
                s = cur[-1]; nxt = shots[shots.index(s) + 1]["t"] if shots.index(s) + 1 < len(shots) else sc["_end"]
                draw_shot(frame, sc, s, t, nxt, punch)
                if t - s["t"] < 0.05 and s is not shots[0]: ab = max(ab, 6)
            if sc.get("label"): draw_label(frame, sc["label"], ti, light)
            if sc.get("counter"): draw_counter(frame, sc["counter"], ti, dur, light)
            if sc.get("big"): draw_big(frame, sc["big"], ti, light)
            if sc.get("tag"): shake = max(shake, draw_tag(frame, sc["tag"], ti - 0.15))
            if sc.get("hit") and ti < 0.25:
                shake = max(shake, 1 - ti / 0.25); ab = max(ab, 18 * (1 - ti / 0.25))
            draw_caption(frame, G["groups"][scenes.index(sc)], t, light)
            if sc.get("hit") and ti < 0.12:
                frame.alpha_composite(Image.new("RGBA", (W, H), (230, 245, 255, int(200 * (1 - ti / 0.12)))))
        else:
            outro(frame, t - outro_t, brand)
        frame = frame.convert("RGB")
        if ab >= 1: frame = chroma(frame, ab)
        if shake > 0:
            frame = frame.transform((W, H), Image.AFFINE, (1, 0, srng.uniform(-1, 1) * 20 * shake, 0, 1, srng.uniform(-1, 1) * 20 * shake), resample=Image.BILINEAR)
        ff.stdin.write(frame.tobytes())
    ff.stdin.close(); ff.wait()
    return path


def render(script_path, out_path, workers=4):
    import audio2
    script = json.load(open(script_path))
    work = os.path.splitext(out_path)[0] + "_work"
    scenes, clips, total = build(script, work)
    bpm = script.get("bpm", 185); beat_s = 60 / bpm
    drop_t = next((sc["_start"] for sc in scenes if sc.get("drop")), scenes[min(2, len(scenes) - 1)]["_start"])
    music = script.get("music")
    music_offset = 0.0
    if music:  # external track: align its drop with ours, cut on its real beats
        mb = json.load(open(os.path.join(S, music["beats"])))
        beat_s = float(np.median(np.diff(mb["beats"])))
        if "offset" in music:
            music_offset = music["offset"]
        else:
            mdrop = min((b for b in mb["beats"] if b >= music["drop"] - 0.05), key=lambda b: b)
            music_offset = max(0.0, mdrop - drop_t)
        bl = list(mb["beats"])
        while bl[-1] - music_offset < total: bl.append(bl[-1] + beat_s)  # extrapolate past the clip
        grid = [b - music_offset for b in bl if 0 <= b - music_offset <= total]
    else:
        grid = [drop_t + k * beat_s for k in range(-int(drop_t / beat_s), int((total - drop_t) / beat_s) + 1)]
    plan_shots(scenes, script.get("seed", 1), shot_len=script.get("beats_per_shot", 2) * beat_s, grid=grid)
    outro_t = scenes[-1]["_end"]
    kw = [tok[2] for sc in scenes for tok in sc["_tokens"] if tok[1] != "plain"]
    events = [dict(t=0.0, kind="hit"), dict(t=outro_t, kind="hit")]
    for sc in scenes:
        if sc.get("hit") and sc["_start"] > 0: events.append(dict(t=sc["_start"], kind="hit"))
        if sc.get("tag"): events.append(dict(t=sc["_start"] + 0.29, kind="tag"))
        for sh in sc["_shots"][1:] + ([sc["_shots"][0]] if sc["_shots"] and sc["_start"] > 0 and not sc.get("hit") else []):
            events.append(dict(t=sh["t"], kind="cut"))
    breaks = [(sc["_start"], sc["_end"]) for sc in scenes if sc.get("break")]
    wav = f"{work}/mix.wav"
    audio2.mix(clips, total, events, wav, drop_t, seed=script.get("seed", 1), breaks=breaks, bpm=bpm,
               music_file=os.path.join(S, music["file"]) if music and music.get("file") else None, music_offset=music_offset,
               music_vol=script.get("music_vol", 0.28))
    n = int(total * FPS)
    state = dict(music=bool(music), drop_t=drop_t, beat=beat_s, beats=sorted(g for g in grid if g >= (0 if music else drop_t - 0.01)), scenes=scenes, total=total, outro_t=outro_t, kw=kw, brand=script.get("brand", "COTIDIE"),
                 groups=[caption_groups(sc["_tokens"]) for sc in scenes])
    chunks = [(i * n // workers, (i + 1) * n // workers, f"{work}/part{i}.mp4") for i in range(workers)]
    with Pool(workers, initializer=init_worker, initargs=(state,)) as p:
        parts = p.map(render_range, chunks)
    lst = f"{work}/parts.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(x)}'\n" for x in parts))
    for suffix, a in (("", wav), ("_sans_musique", wav[:-4] + "_nomusic.wav")):
        o = out_path[:-4] + suffix + ".mp4"
        subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", a,
                               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", o])
    json.dump(dict(title=script.get("title"), caption=script.get("caption"), duration=round(total, 1)),
              open(out_path[:-4] + ".json", "w"), ensure_ascii=False, indent=1)
    print("done", out_path, f"{total:.1f}s")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
