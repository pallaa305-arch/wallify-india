#!/usr/bin/env python3
"""Backwards-compat shim for daily.py / gen_real.py.
Pollinations free API, no key needed.
API: generate_image(prompt, width, height, model) -> dict(success, image, error_type)
"""
import os, sys, time, tempfile, urllib.request, urllib.parse, json
from pathlib import Path

MODEL_MAP = {"flux": "flux", "turbo": "turbo", "default": "flux"}

def generate_image(prompt: str, width: int = 1080, height: int = 1920,
                   model: str = "flux", **kwargs) -> dict:
    m = MODEL_MAP.get(model, model)
    q = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{q}?width={width}&height={height}&model={m}&nologo=true"
    tmp = Path(tempfile.gettempdir()) / f"wgen_{int(time.time()*1000)}.jpg"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        if len(data) < 1000:
            return {"success": False, "error_type": "tiny_response",
                    "error": f"only {len(data)} bytes"}
        tmp.write_bytes(data)
        return {"success": True, "image": str(tmp),
                "width": width, "height": height, "model": m}
    except Exception as e:
        return {"success": False, "error_type": type(e).__name__, "error": str(e)[:200]}

if __name__ == "__main__":
    # tiny self-test
    r = generate_image("red apple", 512, 512, "flux")
    print(json.dumps(r, indent=2))