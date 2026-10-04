"""
pipeline.py
Input image -> Image recognition -> Knowledge-base matching ->
IF-THEN rule evaluation -> Traffic sign identification -> Meaning + instruction
"""
from PIL import Image

import rules as rule_engine


def identify(image, kb, recognizer):
    if isinstance(image, str):
        image = Image.open(image)

    # 1. image recognition
    candidates = recognizer.match(image, top_k=5)
    best_id, confidence = candidates[0]

    # 2. knowledge-base matching
    sign = kb.get(best_id)

    # 3. IF-THEN rule evaluation
    facts = {"sign_id": best_id, "sign_name": sign["name"], "category": sign["category"],
             "confidence": confidence}
    facts, fired = rule_engine.infer(facts, kb.rules)

    recognized = facts.get("status") == "RECOGNIZED"
    return {
        "recognized": recognized,
        "sign_id": best_id,
        "name": sign["name"] if recognized else "UNKNOWN",
        "category": sign["category"] if recognized else "-",
        "description": sign["description"] if recognized else "-",
        "meaning": sign["meaning"] if recognized else "-",
        "instruction": facts.get("instruction", ""),
        "related_rules": sign["rules"] if recognized else "-",
        "category_rule": facts.get("category_rule", ""),
        "legal_note": facts.get("legal_note", ""),
        "confidence": confidence,
        "image": sign["image"],
        "alternatives": [{"sign_id": i, "name": kb.get(i)["name"], "score": sc} for i, sc in candidates[1:]],
        "fired_rules": [{"rule_id": r["rule_id"], "text": r["text"]} for r in fired],
    }
