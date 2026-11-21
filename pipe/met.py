"""Search The Met Open Access (CC0) and download candidate images."""
import json, os, sys, urllib.parse, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
BASE = "https://collectionapi.metmuseum.org/public/collection"
def get(url):
    for t in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60) as r:
                return r.read()
        except Exception as e:
            if t == 3: raise
            time.sleep(2 + 3 * t)
def search(q, n=8, dept=None):
    p = dict(q=q, hasImages="true", limit=40)
    if dept: p["departmentId"] = dept
    ids = json.loads(get(f"{BASE}/v1.1/search?" + urllib.parse.urlencode(p))).get("objectIDs") or []
    out = []
    def fetch(i):
        try: return json.loads(get(f"{BASE}/v1/objects/{i}"))
        except Exception: return None
    with ThreadPoolExecutor(8) as ex:
        for o in ex.map(fetch, ids[:30]):
            if o and o.get("isPublicDomain") and o.get("primaryImageSmall"):
                out.append(o)
            if len(out) >= n: break
    return out
if __name__ == "__main__":
    outdir, queries = sys.argv[1], json.loads(sys.argv[2])
    os.makedirs(outdir, exist_ok=True)
    mp = os.path.join(outdir, "meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    for key, spec in queries.items():
        q, dept = (spec, None) if isinstance(spec, str) else spec
        for i, o in enumerate(search(q, dept=dept)):
            fn = f"{key}_{i}.jpg"
            open(os.path.join(outdir, fn), "wb").write(get(o["primaryImageSmall"]))
            meta[fn] = dict(id=o["objectID"], title=o["title"], full=o["primaryImage"], url=o["objectURL"], date=o.get("objectDate"))
        print(key, "done", flush=True)
    json.dump(meta, open(mp, "w"), indent=1, ensure_ascii=False)
