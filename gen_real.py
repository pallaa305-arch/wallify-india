#!/usr/bin/env python3
"""
Wallify Real Wallpaper Generator — Pollinations backend.
Generates REAL AI images (bikes, cars, superheroes, etc.) into
public/assets/, replacing the old generative PNGs.

Rate-limit aware: sleeps between calls, retries on 429.
Usage: python gen_real.py
"""
import os, sys, time, json, shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = Path("C:/Users/Dell/AppData/Local/hermes/hermes-agent/tools")
sys.path.insert(0, str(TOOLS))
from generate_image import generate_image

ASSETS = HERE / "public" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# --- Categories: (folder, [prompt templates]) ---
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
        "A astronaut {n} floating in space, earth below, sun flare, 8k",
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

PER_CAT = 15
W, H = 1080, 1920  # mobile wallpaper
MODEL = "flux"

def gen_one(cat, idx, tmpl):
    prompt = tmpl.format(n=idx+1)
    res = generate_image(prompt, width=W, height=H, model=MODEL)
    if res["success"]:
        src = Path(res["image"])
        dst = ASSETS / f"{cat}_{idx+1:03d}.jpg"
        shutil.copy(src, dst)
        return True, str(dst)
    return False, res.get("error_type", "err")

def main():
    # Clear old generative PNGs (keep nothing from old set)
    old = list(ASSETS.glob("*.png"))
    for f in old:
        f.unlink()
    print(f"Cleared {len(old)} old PNGs")

    manifest = []
    total, ok = 0, 0
    for cat, tmpls in CATEGORIES.items():
        print(f"\n=== Category: {cat} ===")
        for i in range(PER_CAT):
            tmpl = tmpls[i % len(tmpls)]
            success, info = gen_one(cat, i, tmpl)
            total += 1
            if success:
                ok += 1
                manifest.append({
                    "file": f"{cat}_{i+1:03d}.jpg",
                    "category": cat,
                    "w": W, "h": H,
                })
                print(f"  [{ok}/{total}] {cat}_{i+1:03d}.jpg OK")
            else:
                print(f"  [{total}] {cat}_{i+1:03d} FAIL ({info}) — retry once")
                time.sleep(10)
                success, info = gen_one(cat, i, tmpl)
                if success:
                    ok += 1
                    manifest.append({"file": f"{cat}_{i+1:03d}.jpg", "category": cat, "w": W, "h": H})
                    print(f"  retry OK")
                else:
                    print(f"  retry FAIL — skip")
            # rate-limit friendly pause
            time.sleep(5)

    # Write manifest
    (ASSETS / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"\n=== DONE: {ok}/{total} wallpapers generated ===")
    print(f"Manifest: {len(manifest)} entries")

if __name__ == "__main__":
    main()
