#!/usr/bin/env python3
"""Daily wallpaper generator: adds 10 new wallpapers (1 per category rotating),
updates manifest, commits & pushes to GitHub so Render auto-deploys."""
import os, random, subprocess, json, sys
sys.path.insert(0, os.path.dirname(__file__))
from generate import GENERATORS, PALETTES, generate_one, OUT

CATS = list(PALETTES.keys())

def main():
    n = 10
    # rotate category per day so all categories grow evenly
    day = int(__import__('datetime').datetime.now().strftime("%j"))
    picks = [CATS[i % len(CATS)] for i in range(n)]  # 1 each of 10 cats
    random.seed(day * 1000 + 7)  # deterministic-but-daily-unique
    added = []
    man = os.path.join(OUT, "manifest.json")
    data = json.load(open(man)) if os.path.exists(man) else []
    existing = {(x["cat"], x["seed"]) for x in data}
    for cat in picks:
        # find a fresh seed
        for attempt in range(50):
            seed = random.randint(10000, 99999)
            if (cat, seed) not in existing:
                break
        r = generate_one(cat, seed)
        added.append(r)
        data.append(r)
        existing.add((cat, seed))
    json.dump(data, open(man, "w"), indent=0)
    print(f"Added {len(added)} wallpapers: {[a['name'] for a in added]}")
    # git push
    subprocess.run(["git","add","-A"], cwd=os.path.dirname(__file__))
    subprocess.run(["git","commit","-q","-m",f"Daily: +{len(added)} wallpapers ({len(data)} total)"], cwd=os.path.dirname(__file__))
    res = subprocess.run(["git","push","origin","main"], cwd=os.path.dirname(__file__), capture_output=True, text=True)
    print("PUSH:", res.returncode, res.stderr[-200:] if res.returncode else "ok")

if __name__ == "__main__":
    main()
