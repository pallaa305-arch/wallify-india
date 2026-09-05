#!/usr/bin/env python3
"""Local driver: runs the same logic daily.py expects, but uses our local shim
that talks to Pollinations (no hermes tool dep). Generates 10 wallpapers,
updates manifest, commits and pushes."""
import os, sys, time, json, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from _shim_generate_image import generate_image

ASSETS = HERE / "public" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920
MODEL = "flux"

CATEGORIES = {
    "superbikes": [
        "A cinematic superbike {n}, glossy red body, studio lighting, reflective floor, 8k product shot",
        "A futuristic sport bike {n} speeding on mountain highway at sunset, motion blur, dramatic",
        "Close-up of a superbike engine {n}, chrome details, mechanical beauty, dark background",
    ],
    "cars": [
        "A luxury sports car {n}, sleek design, neon city night reflection, cinematic 8k",
        "A classic muscle car {n} on desert road, golden hour, vintage vibe",
        "A futuristic concept car {n}, glowing accents, sci-fi tunnel, ultra detailed",
    ],
    "superheroes": [
        "A Marvel-style superhero {n} in dynamic pose, cape flowing, city backdrop, cinematic",
        "A dark armored superhero {n} with glowing eyes, rain, neon city, 8k render",
        "A cute chibi superhero {n}, vibrant colors, comic book style",
    ],
    "nature": [
        "A serene mountain lake {n} at sunrise, mist, reflection, photorealistic",
        "A dense rainforest waterfall {n}, lush green, sunlight rays, 8k",
        "A snowy pine forest {n} under aurora borealis, magical night",
    ],
    "space": [
        "A nebula galaxy {n}, vibrant cosmic colors, stars, deep space photography",
        "A futuristic spaceship {n} near a ringed planet, sci-fi art, cinematic",
        "An astronaut {n} floating in space, earth below, sun flare, 8k",
    ],
    "abstract": [
        "A fluid abstract art {n}, flowing colors, gold and purple, wallpaper aesthetic",
        "A geometric minimalist pattern {n}, dark theme, neon lines",
        "A liquid chrome abstract {n}, mirror finish, studio lighting",
    ],
    "anime": [
        "An anime girl {n} in cherry blossom field, soft lighting, studio ghibli style",
        "A neon cyberpunk anime city {n}, rain, vibrant, wallpaper",
        "A fierce anime warrior {n}, sword, ember particles, dramatic",
    ],
    "gaming": [
        "A cyberpunk game character {n}, neon armor, fps video game art",
        "A fantasy RPG dragon {n}, epic battle scene, volumetric light",
        "A retro arcade neon grid {n}, synthwave aesthetic, 80s vibe",
    ],
    "cars_classic": [
        "A vintage rolls royce {n}, black elegant, mansion driveway, golden hour",
        "A 60s muscle car {n}, chrome bumper, Route 66, nostalgic",
    ],
    "superbikes_stunt": [
        "A stunt rider {n} on superbike, jumping, sparks, action shot",
        "A superbike {n} leaning in race corner, blurred track, speed",
    ],
}

def gen_one(cat, idx, tmpl):
    prompt = tmpl.format(n=idx + 1)
    res = generate_image(prompt, width=W, height=H, model=MODEL)
    if res["success"]:
        src = Path(res["image"])
        dst = ASSETS / f"{cat}_{idx+1:03d}.jpg"
        shutil.copy(src, dst)
        return True, str(dst)
    return False, res.get("error_type", "err")

def main():
    man = ASSETS / "manifest.json"
    data = json.load(open(man)) if man.exists() else []

    maxidx = {}
    for x in data:
        c = x.get("category")
        f = x.get("file", "")
        if c and f.startswith(c + "_"):
            try:
                num = int(f[len(c) + 1:].split(".")[0])
                maxidx[c] = max(maxidx.get(c, 0), num)
            except Exception:
                pass

    cats = list(CATEGORIES.keys())
    n = 10
    added = []
    for i in range(n):
        cat = cats[i % len(cats)]
        cur = maxidx.get(cat, 0)
        tmpl = CATEGORIES[cat][cur % len(CATEGORIES[cat])]
        success, info = gen_one(cat, cur, tmpl)
        if not success:
            print(f"  {cat} FAIL ({info}) - retry once", flush=True)
            time.sleep(10)
            success, info = gen_one(cat, cur, tmpl)
        if success:
            maxidx[cat] = cur + 1
            entry = {"file": f"{cat}_{cur+1:03d}.jpg", "category": cat, "w": W, "h": H}
            data.append(entry)
            added.append(entry["file"])
            print(f"  + {entry['file']} OK", flush=True)
        else:
            print(f"  {cat} retry FAIL - skip", flush=True)
        time.sleep(3)

    json.dump(data, open(man, "w"), indent=2)
    print(f"Added {len(added)} wallpapers. Total now: {len(data)}", flush=True)

    subprocess.run(["git", "add", "-A"], cwd=str(HERE))
    subprocess.run(["git", "commit", "-q", "-m",
                    f"Daily: +{len(added)} wallpapers ({len(data)} total)"],
                   cwd=str(HERE))
    res = subprocess.run(["git", "push", "origin", "main"],
                         cwd=str(HERE), capture_output=True, text=True)
    print("PUSH:", res.returncode,
          (res.stderr or res.stdout)[-300:] if res.returncode else "ok",
          flush=True)

if __name__ == "__main__":
    main()