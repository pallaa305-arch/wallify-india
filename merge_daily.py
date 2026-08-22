#!/usr/bin/env python3
"""Idempotent merge: add any on-disk *_NNN.jpg not yet in the manifest,
write manifest, commit & push. No image generation here (fast)."""
import json, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "public" / "assets"
W, H = 1080, 1920

CATS = ["superbikes","cars","superheroes","nature","space","abstract",
        "anime","gaming","cars_classic","superbikes_stunt"]

man = ASSETS / "manifest.json"
data = json.load(open(man)) if man.exists() else []
existing = {x["file"] for x in data}

maxidx = {}
for x in data:
    c = x.get("category"); f = x.get("file", "")
    if c and f.startswith(c + "_"):
        try:
            num = int(f[len(c)+1:].split(".")[0])
            maxidx[c] = max(maxidx.get(c, 0), num)
        except Exception:
            pass

added = []
for cat in CATS:
    cur = maxidx.get(cat, 0)
    fname = f"{cat}_{cur+1:03d}.jpg"
    if fname in existing:
        continue
    if not (ASSETS / fname).exists():
        print("MISSING ON DISK (skipped):", fname)
        continue
    data.append({"file": fname, "category": cat, "w": W, "h": H})
    existing.add(fname)
    added.append(fname)
    print("+", fname)

json.dump(data, open(man, "w"), indent=2)
print(f"Added {len(added)} to manifest. Total now: {len(data)}")

subprocess.run(["git", "add", "-A"], cwd=str(HERE))
subprocess.run(["git", "commit", "-q", "-m",
                f"Daily: +{len(added)} wallpapers ({len(data)} total)"],
               cwd=str(HERE))
res = subprocess.run(["git", "push", "origin", "main"],
                     cwd=str(HERE), capture_output=True, text=True)
print("PUSH:", res.returncode, res.stderr[-300:] if res.returncode else "ok")
