"""
generate_samples.py - makes example INPUT images in sample_inputs/
Each reference sign is placed on a random background, slightly rotated,
resized, brightened/darkened and given a little noise, so the inputs are NOT
identical to the stored reference images.  File name = <sign_id>_sample.jpg
Run:  python generate_samples.py
"""
import os
import random

import numpy as np
from PIL import Image, ImageEnhance

import config


def make_sample(ref, rng):
    size = 300
    bg_color = rng.choice([(200, 200, 200), (120, 160, 110), (150, 190, 230), (90, 90, 95), (225, 215, 190), (255, 255, 255)])
    bg = Image.new("RGB", (size, size), bg_color)
    k = rng.uniform(0.82, 0.98)
    s = int(size * k)
    sign = ref.resize((s, s), Image.LANCZOS).rotate(rng.uniform(-6, 6), resample=Image.BICUBIC, expand=False, fillcolor=(255, 255, 255))
    off = (rng.randint(0, size - s), rng.randint(0, size - s))
    bg.paste(sign, off)
    bg = ImageEnhance.Brightness(bg).enhance(rng.uniform(0.8, 1.2))
    arr = np.asarray(bg, dtype=np.float32) + np.random.default_rng(rng.randint(0, 10**6)).normal(0, 6, (size, size, 3))
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"))


def main():
    os.makedirs(config.SAMPLE_DIR, exist_ok=True)
    rng = random.Random(42)
    files = sorted(f for f in os.listdir(config.REFERENCE_DIR) if f.endswith(".jpg"))
    for f in files:
        ref = Image.open(os.path.join(config.REFERENCE_DIR, f)).convert("RGB")
        make_sample(ref, rng).save(os.path.join(config.SAMPLE_DIR, f[:-4] + "_sample.jpg"), quality=92)
    print(f"Generated {len(files)} sample input images in {config.SAMPLE_DIR}")


if __name__ == "__main__":
    main()
