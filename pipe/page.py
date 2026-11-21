"""Daily delivery page (HTML) for the Claude Artifact: video + cover + text to copy.

Usage: python3 page.py videos/NNN_slug.json out/NNN_slug_page.html
The page references video.mp4 and couverture.jpg published next to it.
"""
import html, json, sys

d = json.load(open(sys.argv[1]))
title = d.get("title", "Vidéo du jour")
desc = d.get("description") or d.get("caption", "")
tags = " ".join(d.get("hashtags", []))
to_copy = f"{desc}\n\n{tags}".strip()
num = sys.argv[1].split("/")[-1].split("_")[0]

page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cotidie {html.escape(num)}</title>
<style>
:root {{ --bg:#eef3f7; --card:#ffffff; --ink:#0b1016; --muted:#56626e; --accent:#0a5bd6; --line:#d5dde4; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#06080c; --card:#0e141c; --ink:#eef4f8; --muted:#94a3b0; --accent:#6edeff; --line:#1d2833; }} }}
:root[data-theme="dark"] {{ --bg:#06080c; --card:#0e141c; --ink:#eef4f8; --muted:#94a3b0; --accent:#6edeff; --line:#1d2833; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.5 system-ui,-apple-system,sans-serif; }}
main {{ max-width:520px; margin:0 auto; padding:20px 16px 48px; }}
h1 {{ font-size:22px; margin:4px 0 2px; }}
.sub {{ color:var(--muted); font-size:14px; margin-bottom:16px; }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:14px; margin:14px 0; }}
h2 {{ font-size:13px; letter-spacing:.08em; text-transform:uppercase; color:var(--accent); margin:0 0 10px; }}
video, img {{ width:100%; border-radius:10px; display:block; background:#000; }}
pre {{ white-space:pre-wrap; word-wrap:break-word; font:15px/1.5 system-ui,sans-serif; margin:0 0 10px; }}
a.btn, button {{ display:inline-block; width:100%; text-align:center; padding:12px; border-radius:10px; border:0;
  background:var(--accent); color:var(--bg); font-weight:700; font-size:15px; text-decoration:none; cursor:pointer; margin-top:10px; }}
.hint {{ color:var(--muted); font-size:13px; margin-top:8px; }}
ol {{ padding-left:20px; margin:0; }} li {{ margin:4px 0; }}
</style></head>
<body><main>
<h1>{html.escape(title)}</h1>
<div class="sub">Vidéo {html.escape(num)} · @cotidie.mentalite · à publier à 18h30</div>

<div class="card"><h2>1 · Vidéo (sans musique)</h2>
<video src="video.mp4" controls playsinline preload="metadata" poster="couverture.jpg"></video>
<button class="dl" type="button" data-src="video.mp4" data-name="cotidie_{html.escape(num)}.mp4" hidden>Enregistrer la vidéo</button>
<div class="hint">Si le bouton n'apparaît pas : appui long sur la vidéo → Enregistrer.</div></div>

<div class="card"><h2>2 · Texte à copier</h2>
<pre id="t">{html.escape(to_copy)}</pre>
<button id="c" type="button">Copier le texte</button></div>

<div class="card"><h2>3 · Couverture</h2>
<img src="couverture.jpg" alt="Couverture TikTok">
<button class="dl" type="button" data-src="couverture.jpg" data-name="cotidie_{html.escape(num)}_couverture.jpg" hidden>Enregistrer la couverture</button>
<div class="hint">Ou appui long sur l'image → Enregistrer.</div></div>

<div class="card"><h2>Publier</h2><ol>
<li>Importer la vidéo dans TikTok.</li>
<li>Son : <b>revolt</b> (kil krook), démarrage au début, volume 30-40 %.</li>
<li>Modifier la couverture → ajouter depuis la galerie.</li>
<li>Coller le texte.</li>
<li>Cocher « contenu généré par IA » et publier à 18h30.</li></ol></div>
</main>
<script>
(async () => {{
  const downloads = await (window.claude && window.claude.use ? window.claude.use("downloads") : null);
  if (!downloads) return;
  document.querySelectorAll('button.dl').forEach(b => {{
    b.hidden = false;
    const label = b.textContent;
    b.addEventListener('click', async () => {{
      b.disabled = true; b.textContent = 'Préparation…';
      try {{
        const blob = await (await fetch(b.dataset.src)).blob();
        await downloads.save({{ filename: b.dataset.name, data: blob }});
        b.textContent = 'Enregistré ✓';
      }} catch (e) {{
        b.textContent = (e && e.code === 'declined') ? label : 'Indisponible ici';
      }}
      setTimeout(() => {{ b.textContent = label; b.disabled = false; }}, 2500);
    }});
  }});
}})();
document.getElementById('c').addEventListener('click', async () => {{
  const b = document.getElementById('c'), txt = document.getElementById('t').innerText;
  try {{ await navigator.clipboard.writeText(txt); b.textContent = 'Copié ✓'; }}
  catch (e) {{ const r = document.createRange(); r.selectNodeContents(document.getElementById('t'));
    const s = getSelection(); s.removeAllRanges(); s.addRange(r); b.textContent = 'Texte sélectionné : copiez-le'; }}
  setTimeout(() => b.textContent = 'Copier le texte', 2500);
}});
</script></body></html>
"""
open(sys.argv[2], "w").write(page)
print(sys.argv[2])
