#!/usr/bin/env python3
"""
Wallify India - Generative Wallpaper Engine
Produces real PNG wallpapers using numpy/PIL (p5.js-grade algorithms baked to disk).
Categories: gradient, abstract, minimal, dark, nature, geometric, flow, neon, marble, bokeh
Each wallpaper is a unique seed-driven composition.
"""
import os, math, random, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

OUT = os.path.join(os.path.dirname(__file__), "public", "assets")
os.makedirs(OUT, exist_ok=True)

W, H = 1080, 1920  # phone portrait

PALETTES = {
    "gradient": [("#ff8a00","#ff2d7e"),("#00d4aa","#0066ff"),("#7c3aed","#db2777"),
                 ("#f59e0b","#ef4444"),("#06b6d4","#3b82f6"),("#ec4899","#8b5cf6")],
    "abstract": [("#7c3aed","#db2777","#00d4aa"),("#0ea5e9","#6366f1","#ec4899"),
                 ("#f43f5e","#f59e0b","#10b981"),("#6366f1","#06b6d4","#84cc16")],
    "minimal": [("#f5f5f0","#ff8a00"),("#ffffff","#111111"),("#eef2f7","#3b82f6"),
                ("#1a1a1a","#f5f5f0"),("#fafafa","#e11d48")],
    "dark": [("#0a0e1a","#1a1f3e"),("#05060f","#2a2f55"),("#0d1117","#161b22"),
             ("#000000","#1f2937"),("#0a0a0f","#2d1b4e")],
    "nature": [("#134e2e","#0a2618"),("#0ea5e9","#e0f7fa"),("#166534","#bbf7d0"),
               ("#7c2d12","#fef3c7"),("#065f46","#a7f3d0")],
    "geometric": [("#1e1b4b","#8b5cf6"),("#0f172a","#38bdf8"),("#1c1917","#f59e0b"),
                  ("#172554","#60a5fa"),("#18181b","#f43f5e")],
    "flow": [("#0a0e1a","#00d4aa","#0066ff"),("#0d1117","#f43f5e","#f59e0b"),
             ("#05060f","#7c3aed","#06b6d4"),("#1a1a1a","#10b981","#84cc16")],
    "neon": [("#0a0e1a","#ff00ff","#00ffff"),("#000000","#39ff14","#ff1493"),
             ("#05060f","#ff6ec7","#00ffe7"),("#0a0a0f","#ffe600","#ff2d95")],
    "marble": [("#fafafa","#e5e7eb","#9ca3af"),("#fffbeb","#fde68a","#d97706"),
               ("#f8fafc","#cbd5e1","#64748b"),("#fef2f2","#fecaca","#dc2626")],
    "bokeh": [("#1e1b4b","#8b5cf6","#ec4899"),("#0f172a","#38bdf8","#22d3ee"),
              ("#18181b","#f59e0b","#ef4444"),("#172554","#60a5fa","#818cf8")],
}

def make_grad(c0, c1):
    arr = np.zeros((H, W, 3), dtype=np.float32)
    t = np.linspace(0, 1, H)[:, None]
    for i, (a, b) in enumerate(zip(hex2rgb(c0), hex2rgb(c1))):
        arr[:, :, i] = (a + (b - a) * t)
    # diagonal blend variant
    return arr

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb2hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(x))) for x in rgb)

def add_noise(arr, amt=8):
    n = (np.random.rand(*arr.shape) - 0.5) * amt
    return np.clip(arr + n, 0, 255).astype(np.uint8)

def gen_gradient(seed, pal):
    rnd = random.Random(seed)
    c0, c1 = rnd.choice(pal)
    arr = make_grad(c0, c1)
    # radial option
    if rnd.random() < 0.5:
        cx, cy = rnd.randint(200, 880), rnd.randint(400, 1500)
        Y, X = np.mgrid[0:H, 0:W]
        d = np.sqrt((X-cx)**2 + (Y-cy)**2) / 1200
        d = np.clip(d, 0, 1)[:, :, None]
        arr = arr * (1 - d) + np.array(hex2rgb(c1), np.float32) * d
    img = Image.fromarray(np.asarray(arr, np.uint8))
    return img

def gen_abstract(seed, pal):
    rnd = random.Random(seed)
    cols = rnd.choice(pal)
    img = Image.new("RGB", (W, H), cols[0])
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rnd.randint(8, 16)):
        x0, y0 = rnd.randint(0, W), rnd.randint(0, H)
        x1, y1 = rnd.randint(0, W), rnd.randint(0, H)
        col = hex2rgb(cols[rnd.randint(0, len(cols)-1)])
        draw.line([x0, y0, x1, y1], fill=col + (rnd.randint(60, 160),), width=rnd.randint(2, 30))
    for _ in range(rnd.randint(4, 10)):
        x, y = rnd.randint(0, 1000), rnd.randint(0, 1900)
        r = rnd.randint(40, 300)
        c = hex2rgb(cols[rnd.randint(0, len(cols)-1)])
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c + (rnd.randint(30, 120),))
    img = img.filter(ImageFilter.GaussianBlur(rnd.randint(8, 30)))
    return add_noise(np.array(img), 5)

def gen_minimal(seed, pal):
    rnd = random.Random(seed)
    bg, fg = rnd.choice(pal)
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)
    shape = rnd.choice(["circle", "line", "arc", "square"])
    if shape == "circle":
        r = rnd.randint(120, 260); x, y = rnd.randint(r, W-r), rnd.randint(r, H-r)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=fg)
    elif shape == "line":
        y = rnd.randint(800, 1100)
        draw.rectangle([80, y, W-80, y+rnd.randint(4, 10)], fill=fg)
    elif shape == "arc":
        draw.arc([100, 600, W-100, 1400], 20, 320, fill=fg, width=rnd.randint(6, 20))
    else:
        s = rnd.randint(200, 400)
        x = rnd.randint(100, W-s-100); y = rnd.randint(600, H-s-200)
        draw.rectangle([x, y, x+s, y+s], outline=fg, width=rnd.randint(4, 12))
    return np.array(img)

def gen_dark(seed, pal):
    rnd = random.Random(seed)
    c0, c1 = rnd.choice(pal)
    arr = make_grad(c0, c1)
    Y, X = np.mgrid[0:H, 0:W]
    # stars
    img = Image.fromarray(arr.astype(np.uint8))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rnd.randint(80, 200)):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        b = rnd.randint(80, 255)
        draw.point((x, y), fill=(b, b, b, rnd.randint(40, 200)))
    if rnd.random() < 0.6:
        cx, cy = rnd.randint(700, 1000), rnd.randint(200, 500)
        draw.ellipse([cx-90, cy-90, cx+90, cy+90], fill=(255, 255, 255, 230))  # moon
        draw.ellipse([cx-70, cy-110, cx+70, cy+70], fill=hex2rgb(c1)+(255,))  # crescent cut
    return np.array(img)

def gen_nature(seed, pal):
    rnd = random.Random(seed)
    c0, c1 = rnd.choice(pal)
    arr = make_grad(c0, c1)
    img = Image.fromarray(arr.astype(np.uint8))
    draw = ImageDraw.Draw(img, "RGBA")
    # sun
    sx, sy = rnd.randint(200, 880), rnd.randint(200, 700)
    draw.ellipse([sx-80, sy-80, sx+80, sy+80], fill=(255, 240, 180, 200))
    # hills (simple sine layers)
    Y, X = np.mgrid[0:H, 0:W]
    for layer in range(3):
        base = 1100 + layer * 220
        amp = 60 + layer * 30
        col = hex2rgb(c1) if layer % 2 else hex2rgb(c0)
        for x in range(0, W, 4):
            y = int(base + amp * math.sin(x / 180 + layer + seed))
            draw.line([x, y, x+4, H], fill=col + (180 - layer*40,), width=2)
    return np.array(img)

def gen_geometric(seed, pal):
    rnd = random.Random(seed)
    bg, fg = rnd.choice(pal)
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img, "RGBA")
    mode = rnd.choice(["triangles", "circles", "grid", "lines"])
    accent = fg
    if mode == "triangles":
        for _ in range(rnd.randint(10, 25)):
            pts = [(rnd.randint(0, W), rnd.randint(0, H)) for _ in range(3)]
            draw.polygon(pts, fill=hex2rgb(accent) + (rnd.randint(30, 130),))
    elif mode == "circles":
        for _ in range(rnd.randint(12, 30)):
            x, y = rnd.randint(0, W), rnd.randint(0, H); r = rnd.randint(20, 160)
            draw.ellipse([x-r, y-r, x+r, y+r], outline=hex2rgb(accent) + (rnd.randint(80, 200),), width=rnd.randint(2, 6))
    elif mode == "grid":
        for x in range(0, W, rnd.randint(60, 120)):
            draw.line([x, 0, x, H], fill=hex2rgb(accent) + (90,), width=1)
        for y in range(0, H, rnd.randint(60, 120)):
            draw.line([0, y, W, y], fill=hex2rgb(accent) + (90,), width=1)
    else:
        for _ in range(rnd.randint(15, 40)):
            y = rnd.randint(0, H)
            draw.line([0, y, W, y + rnd.randint(-100, 100)], fill=hex2rgb(accent) + (rnd.randint(40, 160),), width=rnd.randint(1, 5))
    img = img.filter(ImageFilter.GaussianBlur(rnd.randint(0, 4)))
    return np.array(img)

def gen_flow(seed, pal):
    rnd = random.Random(seed)
    cols = rnd.choice(pal)
    bg = cols[0]
    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img, "RGBA")
    # flow field particles
    a, b = hex2rgb(cols[1]), hex2rgb(cols[2]) if len(cols) > 2 else hex2rgb(cols[1])
    t = seed * 0.1
    for _ in range(rnd.randint(300, 600)):
        x, y = float(rnd.randint(0, W)), float(rnd.randint(0, H))
        for _ in range(rnd.randint(20, 60)):
            ang = math.sin(x * 0.005 + t) + math.cos(y * 0.005 - t)
            x += math.cos(ang) * 6; y += math.sin(ang) * 6
            if 0 <= x < W and 0 <= y < H:
                c = a if rnd.random() < 0.5 else b
                draw.point((int(x), int(y)), fill=c + (rnd.randint(40, 160),))
    img = img.filter(ImageFilter.GaussianBlur(1))
    return np.array(img)

def gen_neon(seed, pal):
    rnd = random.Random(seed)
    cols = rnd.choice(pal)
    img = Image.new("RGB", (W, H), cols[0])
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rnd.randint(15, 35)):
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        r = rnd.randint(30, 200)
        c = hex2rgb(rnd.choice(cols[1:]))
        draw.ellipse([x-r, y-r, x+r, y+r], outline=c + (220,), width=rnd.randint(2, 6))
        draw.ellipse([x-r//2, y-r//2, x+r//2, y+r//2], outline=c + (120,), width=1)
    img = img.filter(ImageFilter.GaussianBlur(3))
    img = ImageEnhance.Brightness(img).enhance(1.15)
    return np.array(img)

def gen_marble(seed, pal):
    rnd = random.Random(seed)
    cols = rnd.choice(pal)
    arr = np.zeros((H, W), dtype=np.float32)
    # value noise
    for _ in range(6):
        freq = rnd.randint(2, 20); amp = rnd.random()
        ph = rnd.random() * 6.28
        for y in range(H):
            for x in range(W):
                arr[y, x] += amp * math.sin(x / W * freq * 6.28 + ph) * math.cos(y / H * freq * 6.28)
    arr = (arr - arr.min()) / (arr.max() - arr.min())
    base = hex2rgb(cols[0]); mid = hex2rgb(cols[1]); hi = hex2rgb(cols[2])
    out = np.zeros((H, W, 3), dtype=np.uint8)
    for i in range(3):
        out[:, :, i] = (base[i] + (mid[i] - base[i]) * arr + (hi[i] - mid[i]) * (arr**3)).astype(np.uint8)
    return out

def gen_bokeh(seed, pal):
    rnd = random.Random(seed)
    cols = rnd.choice(pal)
    img = Image.new("RGB", (W, H), cols[0])
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rnd.randint(40, 90)):
        x, y = rnd.randint(0, W), rnd.randint(0, H); r = rnd.randint(20, 120)
        c = hex2rgb(rnd.choice(cols[1:]))
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c + (rnd.randint(30, 110),))
    img = img.filter(ImageFilter.GaussianBlur(rnd.randint(20, 50)))
    return np.array(img)

GENERATORS = {
    "gradient": gen_gradient, "abstract": gen_abstract, "minimal": gen_minimal,
    "dark": gen_dark, "nature": gen_nature, "geometric": gen_geometric,
    "flow": gen_flow, "neon": gen_neon, "marble": gen_marble, "bokeh": gen_bokeh,
}

NAMES = {
    "gradient": ["Sunset Blush", "Ocean Deep", "Purple Haze", "Ember", "Aqua Sky", "Rose Quartz"],
    "abstract": ["Prism Storm", "Color Flux", "Neon Bloom", "Spectrum", "Chromatic", "Vivid Drift"],
    "minimal": ["Pure", "Line", "Mono Dot", "Quiet", "Soft Square", "Calm"],
    "dark": ["Midnight", "Void", "Starfield", "Lunar", "Obsidian", "Nightfall"],
    "nature": ["Forest", "Sky", "Meadow", "Sunrise", "Tide", "Verdant"],
    "geometric": ["Tri Grid", "Orbit", "Lattice", "Vector", "Polygon", "Struct"],
    "flow": ["Current", "Stream", "Drift Field", "Tide Lines", "Wave", "Flux"],
    "neon": ["Neon Grid", "Cyber Glow", "Synth", "Laser", "Volt", "Glow"],
    "marble": ["Marble White", "Gold Vein", "Slate", "Pearl", "Stone", "Quartz"],
    "bokeh": ["Bokeh Dream", "Light Orbs", "Soft Glow", "Haze", "Bubble", "Blur"],
}

def generate_one(cat, seed):
    img = GENERATORS[cat](seed, PALETTES[cat])
    nm = rnd_name(cat, seed)
    fname = f"{cat}_{seed:05d}.png"
    path = os.path.join(OUT, fname)
    if not isinstance(img, Image.Image):
        img = Image.fromarray(np.asarray(img, np.uint8))
    img.save(path, "PNG")
    return {"file": fname, "name": nm, "cat": cat, "seed": seed}

def rnd_name(cat, seed):
    rnd = random.Random(seed)
    return f"{rnd.choice(NAMES[cat])} #{seed % 99 + 1}"

if __name__ == "__main__":
    import json, sys
    cat = sys.argv[1] if len(sys.argv) > 1 else "gradient"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    base = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    results = []
    for i in range(n):
        seed = base + i * 7919  # prime step = unique
        results.append(generate_one(cat, seed))
    # append to manifest
    man = os.path.join(OUT, "manifest.json")
    if os.path.exists(man):
        data = json.load(open(man))
    else:
        data = []
    data = [r for r in data if r["cat"] != cat or r["seed"] not in [x["seed"] for x in results]]
    data.extend(results)
    json.dump(data, open(man, "w"), indent=0)
    print(f"Generated {len(results)} in {cat}. Total now: {len(data)}")
