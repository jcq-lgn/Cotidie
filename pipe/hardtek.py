"""Procedural melodic hard tek: sustained supersaw lead, tuned distorted kick.

Original composition generated from code (no samples).
Shape modelled on the user's reference: ~218 BPM, 2-bar held lead notes over a
5-1-5-b6 loop in C# minor (G# C# G# A), long tuned kick tails, gated intro.
"""
import numpy as np
from phonk import lp, hp, bp, put, riser, SR

LEAD_GAIN = 1.5
TUNE = 1.026  # reference sits ~0.45 semitone sharp (sped-up feel)
hz = lambda m: 440 * TUNE * 2 ** ((m - 69) / 12)
# dim7 (D F Ab B, top G#5)  <->  C major (C E G, top E5 / C5); 2 bars each
CHORDS = [[62, 65, 68, 71, 80], [60, 64, 67, 72], [62, 65, 68, 71, 80], [60, 64, 67, 76]]
LOOP = CHORDS
ROOTS = [41, 36, 41, 36]  # kick-tail roots: F, C


def kick(tail_hz, dur):
    t = np.arange(int(dur * SR)) / SR
    f = 140 * np.exp(-t * 40) + tail_hz
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s = np.tanh(s * 1.6)
    e = np.exp(-t * 9)
    e[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    click = hp(np.random.default_rng(1).normal(0, 1, len(t)), 3000) * np.exp(-t * 350) * 0.5
    return lp(s * e, 700) * 0.9 + click


def lead_track(total, t0, notes_dur, gate=None, rng=None):
    """Continuous supersaw following LOOP with light glide and vibrato."""
    n = int(total * SR)
    t = np.arange(n) / SR
    idx = np.floor(np.maximum(t - t0, 0) / notes_dur).astype(int) % len(LOOP)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t)
    out = np.zeros(n)
    rng = rng or np.random.default_rng(0)
    for v in range(5):  # chord voices (voice 4 = top note, louder)
        midi = np.array([c[min(v, len(c) - 1)] if v < len(c) else c[-1] for c in LOOP], float)[idx]
        f = lp(hz(midi), 25)
        g = 1.4 if v == 4 or (v == 3 and False) else 0.8
        for det in (-0.012, 0, 0.012):
            ph = np.cumsum(f * vib * (1 + det)) / SR + rng.random()
            out += (2 * (ph % 1) - 1) * g
    out = lp(hp(out, 150), 3800) / 14
    out = np.tanh(out * 1.8) * 0.5
    if gate is not None: out *= gate
    return out


def beat(total, drop_t, seed=1, bpm=185, breaks=(), build_bars=4):
    rng = np.random.default_rng(seed)
    n = int(total * SR)
    beat_s = 60 / bpm
    note_dur = beat_s * 8  # 2 bars per lead note
    drums = np.zeros(n)
    # lead starts at the top of the track, loop aligned so a phrase begins at the drop
    t0 = drop_t - note_dur * np.ceil(drop_t / note_dur)
    t = np.arange(n) / SR
    # gate: chopped 8ths before the drop, open after (and in breaks: open, softer)
    eighth = beat_s / 2
    chop = ((np.floor((t - t0) / eighth) % 2) == 0).astype(float)
    chop = lp(chop, 60)
    gate = np.where(t < drop_t, 0.35 + 0.65 * chop, 1.0)
    lead = lead_track(total, t0, note_dur, gate, rng)
    # intro filter: muffled lead that opens toward the drop
    di = int(drop_t * SR)
    if di > 0:
        seg = int(0.05 * SR)
        for i in range(0, di, seg):
            fc = 500 + 3500 * (i / di) ** 2
            lead[i:i + seg] = lp(lead[max(0, i - 3000):i + seg], fc)[-len(lead[i:i + seg]):]
    # kicks
    build_start = drop_t - build_bars * 4 * beat_s
    k = 0
    tk = drop_t - np.ceil(drop_t / beat_s) * beat_s
    while tk < total:
        in_break = any(a <= tk < b for a, b in breaks)
        note_i = int(np.floor((tk - t0) / note_dur)) % len(LOOP)
        tail = hz(ROOTS[note_i] - 12) / TUNE
        if tk >= drop_t and not in_break:
            put(drums, kick(tail, beat_s * 0.98), tk)
            # offbeat hat
            put(drums, hp(rng.normal(0, 1, int(0.05 * SR)), 7500) * np.exp(-np.arange(int(0.05 * SR)) / SR * 60) * 0.45, tk + beat_s / 2)
        elif build_start <= tk < drop_t:
            # build: kicks on every other beat, then every beat in the last bar
            last_bar = tk >= drop_t - 4 * beat_s
            if last_bar or round((tk - build_start) / beat_s) % 2 == 0:
                put(drums, kick(tail, beat_s * 0.98) * 0.8, tk)
        tk += beat_s; k += 1
    put(drums, riser(rng, min(drop_t, 3.0)) * 0.8, drop_t - min(drop_t, 3.0))
    for a, b in breaks:  # breaks: lead stays, a bit quieter and darker
        i0, i1 = int(a * SR), int(b * SR)
        lead[i0:i1] = lp(lead[i0:i1], 1800) * 0.9
    # reverb on the lead: convolve with a decaying noise tail
    ir_t = np.arange(int(1.6 * SR)) / SR
    ir = np.random.default_rng(9).normal(0, 1, len(ir_t)) * np.exp(-ir_t * 3.2)
    ir = lp(ir, 5000); ir /= np.abs(ir).sum() / 6
    from scipy.signal import fftconvolve
    wet = fftconvolve(lead, ir)[:n]
    lead = lead * 0.7 + wet * 0.45
    air = hp(rng.normal(0, 1, n), 5000) * 0.03
    mix = lead * LEAD_GAIN + drums * 0.8 + air
    mix = hp(mix, 28)
    mix = np.tanh(mix * 1.5) / np.tanh(1.5)
    return mix / max(1e-6, np.abs(mix).max()) * 0.95
