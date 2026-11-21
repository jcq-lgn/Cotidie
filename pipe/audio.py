"""Voice assembly, synthesized cinematic score + SFX, and final mix."""
import json, subprocess
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100


def duration(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path])
    return float(json.loads(out)["format"]["duration"])


def load(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.float32).copy()


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], "band", fs=SR, output="sos"), x)


def note(freq, dur, rng, harmonics=7, detune=0.0025):
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for d in (-detune, 0, detune):
        f = freq * (1 + d)
        ph = rng.random() * 6.28
        for h in range(1, harmonics + 1):
            out += np.sin(2 * np.pi * f * h * t + ph * h) / h
    return out / 3


def env(n, a, r):
    e = np.ones(n)
    na, nr = min(int(a * SR), n // 2), min(int(r * SR), n // 2)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def score(total, rng, bpm=72):
    n = int(total * SR)
    mus = np.zeros(n)
    beat = 60 / bpm
    bar = beat * 4
    # A minor epic loop: Am - F - C - G  (2 bars each)
    prog = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    seg = bar * 2
    t0, k = 0.0, 0
    while t0 < total:
        chord = prog[k % 4]
        d = min(seg + 1.5, total - t0 + 0.01)
        if d < 0.2: break
        s = sum(note(midi(m), d, rng) for m in chord) + 0.8 * note(midi(chord[0] - 24), d, rng, harmonics=3)
        s *= env(len(s), 1.2, 1.4)
        i = int(t0 * SR)
        mus[i:i + len(s)] += s[: n - i]
        t0 += seg; k += 1
    mus = lp(mus, 900) * 0.22
    # heartbeat kick (lub-dub) after the hook
    kick_t = np.arange(int(0.35 * SR)) / SR
    f = 95 * np.exp(-kick_t * 18) + 42
    kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kick_t * 9)
    t = 2.0
    while t < total - 1.5:
        for off, g in ((0, 1.0), (beat * 0.45, 0.6)):
            i = int((t + off) * SR)
            seg_ = kick[: max(0, n - i)] * g
            mus[i:i + len(seg_)] += seg_ * 0.5
        t += bar / 2
    return mus


def boom(rng):
    t = np.arange(int(2.2 * SR)) / SR
    f = 70 * np.exp(-t * 3) + 28
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    nz = lp(rng.normal(0, 1, len(t)), 1800) * np.exp(-t * 9) * 0.6
    tail = lp(rng.normal(0, 1, len(t)), 500) * np.exp(-t * 2.5) * 0.25
    return (s + nz + tail) * 0.9


def whoosh(rng, d=0.32):
    t = np.arange(int(d * SR)) / SR
    x = bp(rng.normal(0, 1, len(t)), 500, 5000)
    e = (t / d) ** 2.5
    e[-int(0.03 * SR):] *= np.linspace(1, 0, int(0.03 * SR))
    return x * e * 0.22


def thud(rng):
    t = np.arange(int(0.5 * SR)) / SR
    s = np.sin(2 * np.pi * (55 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 10)
    click = bp(rng.normal(0, 1, len(t)), 1500, 7000) * np.exp(-t * 60) * 0.5
    return (s + click) * 0.9


def place(buf, sig, t):
    i = int(t * SR)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= len(buf): return
    m = min(len(sig), len(buf) - i)
    buf[i:i + m] += sig[:m]


def mix(clips, total, events, out_wav, seed=1):
    rng = np.random.default_rng(seed)
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    for path, t in clips:
        place(voice, load(path), t)
    sfx = np.zeros(n)
    for e in events:
        if e["kind"] == "hit": place(sfx, boom(rng), e["t"])
        elif e["kind"] == "stamp": place(sfx, thud(rng), e["t"])
        else: place(sfx, whoosh(rng), e["t"] - 0.3)
    music = score(total, rng)
    music[-int(1.5 * SR):] *= np.linspace(1, 0.3, int(1.5 * SR))
    tmp = out_wav.replace(".wav", "")
    wavfile.write(tmp + "_v.wav", SR, voice.astype(np.float32))
    bed = music + sfx * 0.9
    bed /= max(1e-6, np.abs(bed).max()) * 1.05
    wavfile.write(tmp + "_m.wav", SR, bed.astype(np.float32))
    voice_fx = ("asetrate=44100*0.965,aresample=44100,atempo=1/0.965,"
                "highpass=f=70,equalizer=f=140:t=q:w=1.2:g=4,equalizer=f=3500:t=q:w=1.5:g=2,"
                "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=4,"
                "aecho=0.85:0.5:55|95:0.16|0.09")
    fc = (f"[0:a]{voice_fx},asplit=2[v][sc];"
          f"[1:a]volume=0.38[m];[m][sc]sidechaincompress=threshold=0.05:ratio=6:attack=20:release=350[md];"
          f"[v][md]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-14:TP=-1.5:LRA=9[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", tmp + "_v.wav", "-i", tmp + "_m.wav",
                           "-filter_complex", fc, "-map", "[out]", "-ar", str(SR), "-ac", "2", out_wav])
