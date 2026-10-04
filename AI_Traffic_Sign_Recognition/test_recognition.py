"""
Tests recognition on every image in sample_inputs/ (file name = <sign_id>_sample.jpg)
and prints accuracy.  Run: python test_recognition.py
"""
import os
import sys

import config
import pipeline
from kb import KnowledgeBase
from recognition import ImageRecognizer

kb = KnowledgeBase()
rec = ImageRecognizer(kb)
print("Knowledge base:", len(kb.signs), "signs |", len(kb.rules), "rules |", kb.backend)

if not os.path.isdir(config.SAMPLE_DIR):
    sys.exit("sample_inputs folder not found - extract sample_inputs.zip into the project folder.")
files = sorted(f for f in os.listdir(config.SAMPLE_DIR) if f.endswith("_sample.jpg"))
correct = 0
for f in files:
    expected = f[: -len("_sample.jpg")]
    r = pipeline.identify(os.path.join(config.SAMPLE_DIR, f), kb, rec)
    ok = r["recognized"] and r["sign_id"] == expected
    correct += ok
    print(f"{'PASS' if ok else 'FAIL'}  {f:<34} -> {r['name']:<24} {r['confidence']:>5}%  | {r['instruction']}")
print(f"\nAccuracy: {correct}/{len(files)} = {100 * correct / len(files):.1f}%")
sys.exit(0 if correct == len(files) else 1)
