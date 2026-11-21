"""Search Wikimedia Commons and download candidate images with license info."""
import json, os, sys, urllib.parse, urllib.request
UA = {"User-Agent": "motivation-video-bot/0.1 (personal project)"}
API = "https://commons.wikimedia.org/w/api.php"

import time, urllib.error
def get(url, tries=6):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(1.0)
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or t == tries - 1: raise
            wait = int(e.headers.get("retry-after", "20")) + 2
            print("429, waiting", wait, flush=True); time.sleep(wait)

def search(query, n=6, width=1400):
    params = dict(action="query", format="json", generator="search", gsrsearch=f"{query} filetype:bitmap",
                  gsrnamespace=6, gsrlimit=n, prop="imageinfo", iiprop="url|extmetadata|size",
                  iiurlwidth=width)
    data = json.loads(get(API + "?" + urllib.parse.urlencode(params)))
    pages = sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0))
    out = []
    for p in pages:
        ii = p["imageinfo"][0]; md = ii.get("extmetadata", {})
        out.append(dict(title=p["title"], url=ii.get("thumburl") or ii["url"], page=ii.get("descriptionurl"),
                        license=md.get("LicenseShortName", {}).get("value", "?"),
                        artist=md.get("Artist", {}).get("value", "?")))
    return out

if __name__ == "__main__":
    outdir, queries = sys.argv[1], json.loads(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)
    meta = {}
    for key, q in queries.items():
        for i, c in enumerate(search(q)):
            fn = f"{key}_{i}.jpg"
            try:
                open(os.path.join(outdir, fn), "wb").write(get(c["url"]))
                meta[fn] = c
            except Exception as e:
                print("fail", fn, e)
    json.dump(meta, open(os.path.join(outdir, "meta.json"), "w"), indent=1, ensure_ascii=False)
    print(len(meta), "images")
