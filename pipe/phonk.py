"""Procedural drift-phonk beat: cowbell melody, distorted 808, kick, clap, hats.

Original composition generated from code (no samples), so no rights issues.
"""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100


def _f(kind, f, order=2):
    return butter(order, f, kind, fs=SR, output="sos")


def lp(x, f): return sosfilt(_f("low", f), x)
def hp(x, f): return sosfilt(_f("high", f), x)
def bp(x, lo, hi): return sosfilt(_f("band", [lo, hi]), x)


LEAD = "pluck"


def pluck(semi, dur=0.32):
    """Dark band-limited saw pluck (replaces the cowbell)."""
    t = np.arange(int(dur * SR)) / SR
    f0 = 220 * 2 ** ((semi - 3) / 12)
    s = np.zeros_like(t)
    for d in (-0.004, 0.004):
        for h in range(1, 12):
            if f0 * h > 6000: break
            s += np.sin(2 * np.pi * f0 * (1 + d) * h * t) / h
    s = lp(s, 1400) * np.exp(-t * 9)
    s[:60] *= np.linspace(0, 1, 60)
    return s * 0.32


def cowbell(semi, dur=0.22):
    if LEAD == "pluck": return pluck(semi)
    t = np.arange(int(dur * SR)) / SR
    r = 2 ** (semi / 12)
    sq = lambda f: np.sign(np.sin(2 * np.pi * f * t))
    s = (sq(392 * r) + sq(564 * r)) * 0.5
    s = lp(bp(s, 330 * r, 2400), 1800)
    e = np.exp(-t * 16) * 0.85 + np.exp(-t * 60) * 0.4
    return np.tanh(s * e * 2.2) * 0.5


def bass808(freq, dur, glide_from=None):
    t = np.arange(int(dur * SR)) / SR
    f = np.full_like(t, freq)
    if glide_from:
        g = np.exp(-t * 25)
        f = freq + (glide_from - freq) * g
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 2.2)
    s[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return np.tanh(s * 6.0) * 0.6


def kick():
    t = np.arange(int(0.28 * SR)) / SR
    f = 160 * np.exp(-t * 35) + 48
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14)
    return np.tanh(s * 2.5) * 0.9


def clap(rng):
    t = np.arange(int(0.25 * SR)) / SR
    n = rng.normal(0, 1, len(t))
    e = np.exp(-t * 22)
    for d in (0.0, 0.011, 0.022):
        i = int(d * SR); e[i:i + 80] += 0.8
    return bp(n, 900, 6000) * e * 0.55


def hat(rng, open_=False):
    d = 0.18 if open_ else 0.045
    t = np.arange(int(d * SR)) / SR
    return hp(rng.normal(0, 1, len(t)), 7000) * np.exp(-t * (14 if open_ else 90)) * 0.22


def riser(rng, d):
    t = np.arange(int(d * SR)) / SR
    n = rng.normal(0, 1, len(t))
    out = np.zeros_like(t)
    seg = int(0.05 * SR)
    for i in range(0, len(t), seg):  # sweep the band upward
        k = i / len(t)
        lo = 300 + 5000 * k
        out[i:i + seg] = bp(n[i:i + seg + 2000], lo, lo * 1.8)[: len(out[i:i + seg])]
    return out * (t / d) ** 2 * 0.35


def put(buf, sig, t):
    i = int(t * SR)
    if i >= len(buf) or i + len(sig) <= 0: return
    if i < 0: sig, i = sig[-i:], 0
    m = min(len(sig), len(buf) - i)
    buf[i:i + m] += sig[:m]


def beat(total, drop_t, seed=1, bpm=132, root=38, breaks=()):
    """Return a mono float array. Filtered intro until drop_t, full beat after."""
    rng = np.random.default_rng(seed)
    n = int(total * SR)
    melody, drums, bass = np.zeros(n), np.zeros(n), np.zeros(n)
    step = 60 / bpm / 4
    # two-bar cowbell phrase (semitones relative to F#), None = rest
    phrase = [0, None, 0, 3, None, 0, 7, None, 5, None, 3, None, 0, None, -2, None,
              0, None, 0, 3, None, 0, 7, None, 10, None, 8, 7, 5, None, 3, None]
    prog = [0, 0, -4, -2]  # bass roots per bar (F#, F#, D, E)
    kick_pat = [0, 6, 10]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    # bring the intro in a little before the drop
    start = max(0.0, drop_t - 3.2)
    i = 0
    t = start - (start % (step * 16))
    while t < total:
        s16 = i % 16; bar = (i // 16) % 4
        in_break = any(a <= t < b for a, b in breaks)
        section_b = (i // 128) % 2 == 1
        note = phrase[i % 32]
        if note is not None and section_b and (i % 32) >= 16:
            note = note - 2 if note > 0 else note + 3
        if note is not None:
            put(melody, cowbell(note + prog[bar] * 0), t)
        if t >= drop_t and not in_break:
            if s16 in kick_pat:
                put(drums, kick(), t)
                prev = prog[(bar - 1) % 4]
                put(bass, bass808(hz(root + prog[bar]), step * (4 if s16 != 10 else 6),
                                  glide_from=hz(root + prev + 12) if s16 == 0 else None), t)
            if s16 in (4, 12): put(drums, clap(rng), t)
            if s16 % 2 == 0 or (section_b and bar % 2): put(drums, hat(rng) * (1 if s16 % 2 == 0 else 0.55), t)
            elif s16 in (7, 15) and bar % 2: put(drums, hat(rng) * 0.7, t)
            if s16 == 14 and bar == 3:  # hat roll into next phrase
                for k in range(4): put(drums, hat(rng) * 0.6, t + k * step / 2)
        i += 1; t += step
    # intro: cowbell low-passed + riser until the drop
    mel_full = melody.copy()
    di = int(drop_t * SR)
    if di > 0:
        mel_full[:di] = lp(melody[:di], 900) * 0.8
        put(drums, riser(rng, min(drop_t, 2.5)), drop_t - min(drop_t, 2.5))
    # simple delay on the melody for space
    d = int(step * 3 * SR)
    echo = np.zeros(n); echo[d:] = mel_full[:-d] * 0.28
    mix = mel_full + echo + bass * 0.9 + drums
    mix = np.tanh(mix * 1.3) / np.tanh(1.3)
    return mix / max(1e-6, np.abs(mix).max()) * 0.95
