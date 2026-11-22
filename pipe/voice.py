"""TTS with word timings via edge-tts (free Microsoft neural voices)."""
import asyncio, os, edge_tts
PROXY = os.environ.get("HTTPS_PROXY")

async def _tts(text, out_mp3, voice, rate, pitch):
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, proxy=PROXY, boundary="WordBoundary")
    words = []
    with open(out_mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append(dict(w=ch["text"], t0=ch["offset"] / 1e7, t1=(ch["offset"] + ch["duration"]) / 1e7))
    return words

def tts(text, out_mp3, voice="fr-FR-HenriNeural", rate="-6%", pitch="-8Hz"):
    import time
    for attempt in range(8):  # the free voice service has short outages: back off up to ~3 min
        try:
            words = asyncio.run(_tts(text, out_mp3, voice, rate, pitch))
            if words: return words
            raise RuntimeError("no audio")
        except Exception:
            if attempt == 7: raise
            time.sleep(min(60, 5 * 2 ** attempt))
