"""Mix: processed voice + phonk beat + SFX. Also writes a no-music version."""
import os, subprocess
import numpy as np
from scipy.io import wavfile
from audio import load, duration, boom, whoosh, thud, place, SR
import phonk, hardtek

VOICE_FX = ("highpass=f=75,equalizer=f=200:t=q:w=1.2:g=2,equalizer=f=3000:t=q:w=1.5:g=2,"
            "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=150:makeup=3")


def mix(clips, total, events, out_wav, drop_t, seed=1, breaks=(), bpm=185, music_vol=0.28, music_file=None, music_offset=0.0):
    rng = np.random.default_rng(seed)
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    for path, t in clips:
        place(voice, load(path), t)
    sfx = np.zeros(n)
    for e in events:
        if e["kind"] == "hit": place(sfx, boom(rng) * 0.8, e["t"])
        elif e["kind"] == "tag": place(sfx, thud(rng) * 0.7, e["t"])
        elif e["kind"] == "cut": place(sfx, whoosh(rng, 0.2) * 0.35, e["t"] - 0.2)
    if music_file and not os.path.exists(music_file):
        print('music file absent: rendering without music', music_file); music_file = None
        music = np.zeros(n)
    elif music_file:
        music = load(music_file)[int(music_offset * SR):].astype(np.float64)
        music = np.tile(music, int(np.ceil(n / len(music))))[:n]  # loop short clips (preview only)
        music /= max(1e-6, np.abs(music).max()) / 0.95
    else:
        music = hardtek.beat(total, drop_t, seed=3, bpm=bpm, breaks=breaks)
    fade = int(1.2 * SR)
    music[-fade:] *= np.linspace(1, 0, fade)
    base = out_wav[:-4]
    wavfile.write(base + "_v.wav", SR, voice)
    wavfile.write(base + "_m.wav", SR, music.astype(np.float32))
    wavfile.write(base + "_s.wav", SR, (sfx / max(1e-6, np.abs(sfx).max()) * 0.8).astype(np.float32))
    fc = (f"[0:a]{VOICE_FX},asplit=2[v][sc];"
          f"[1:a]volume={music_vol}[m];[m][sc]sidechaincompress=threshold=0.06:ratio=3:attack=15:release=250[md];"
          "[2:a]volume=0.6[s];"
          "[v][md][s]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95,loudnorm=I=-13:TP=-1:LRA=8[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", base + "_v.wav", "-i", base + "_m.wav", "-i", base + "_s.wav",
                           "-filter_complex", fc, "-map", "[out]", "-ar", str(SR), "-ac", "2", out_wav])
    fc2 = (f"[0:a]{VOICE_FX}[v];[2:a]volume=0.5[s];"
           "[v][s]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[out]")
    subprocess.check_call(["ffmpeg", "-y", "-v", "error", "-i", base + "_v.wav", "-i", base + "_m.wav", "-i", base + "_s.wav",
                           "-filter_complex", fc2, "-map", "[out]", "-ar", str(SR), "-ac", "2", base + "_nomusic.wav"])
