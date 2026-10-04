# AI-Based Traffic Sign Recognition Using Image Recognition

An intelligent traffic-sign recognizer that combines **image recognition**, a **knowledge base (MongoDB)** and
**IF–THEN rule-based reasoning**. No YOLO, no deep learning, no object detection.

```
Input Traffic Sign Image -> Image Recognition -> Knowledge Base Matching
   -> IF-THEN Rule Evaluation -> Traffic Sign Identification -> Display Meaning and Instructions
```

## Contents
| 68 signs/signals | 23 Prohibitory, 10 Mandatory, 4 Priority, 20 Warning, 8 Informatory, 3 Traffic Signals |
|---|---|
| `reference_images/` | one reference image per sign (stop.jpg, no_entry.jpg, speed_limit_40.jpg, ...) |
| `sample_inputs/` | 68 example INPUT images (`<sign>_sample.jpg`) - supplied as a separate zip; keep the folder next to `app.py` |
| `data/` | `knowledge_base.json`, `rules.json` (offline copy of what is stored in MongoDB) |

## Setup
```
python -m venv venv
venv\Scripts\activate          (Windows)     source venv/bin/activate   (Linux/Mac)
pip install -r requirements.txt
python seed_db.py              # loads knowledge base + rules into MongoDB (and data/*.json)
python app.py                  # open http://127.0.0.1:5000
```
MongoDB is optional at run time: if `mongod` is not running the app automatically reads `data/*.json`
Check MongoDB with `python test_mongodb.py`.
Set a different server with the `MONGO_URI` environment variable.

## Run tests / command line
```
python test_recognition.py     # runs all 68 sample inputs, prints PASS/FAIL + accuracy
```

## Files
| File | Purpose |
|---|---|
| `app.py` | Flask web app (dark-theme upload page, result page, `/api/recognize`) |
| `recognition.py` | image recognition (reference-image / template matching) |
| `rules.py` | IF–THEN forward-chaining rule engine |
| `pipeline.py` | connects recognition -> knowledge base -> rules |
| `kb.py` | loads knowledge base (MongoDB, else JSON) |
| `knowledge_base_data.py` | the 68 signs (name, category, description, meaning, instruction, related rules) + rule generator |
| `seed_db.py` | writes knowledge base and rules to MongoDB / JSON |
| `generate_signs.py`, `generate_samples.py` | recreate reference images / sample inputs |
| `config.py` | paths, MongoDB URI, confidence threshold (60 %) |

## How it works
1. **Image recognition** - the input is compared with the reference image of every sign: windows of the
   input (several sizes/positions) are shrunk to 32x32, their RGB values form a vector, and the cosine
   similarity (normalised cross-correlation) with each reference vector is computed. Best match = recognised sign.
   Only direct reference matching is used - no edge/contour/colour-segmentation, no neural network.
2. **Knowledge-base matching** - the matched sign id fetches name, category, description, meaning,
   road instruction and related rules from MongoDB.
3. **IF–THEN rules** (79 rules, stored in MongoDB `rules` collection), fired by forward chaining:
   - `IF the recognized sign is "STOP" THEN display "Stop the vehicle completely before proceeding."` (one rule per sign)
   - `IF category = "Priority" THEN group = "Regulatory"` -> `IF group = "Regulatory" THEN legal note ...` (chained)
   - `IF confidence < 60% THEN sign = UNKNOWN` (rejects non-sign images)
4. **Output** - sign image, name, category, meaning, road instruction, related rules, confidence, rules fired.

Example (input `stop_sample.jpg`):
```
Sign: STOP | Category: Priority | Meaning: Vehicles must come to a complete halt.
Instruction: Stop the vehicle completely before proceeding.
Rules fired: SIGN-STOP -> CAT-PRIORITY -> GROUP-REGULATORY
```

## Results and limitations
* 68/68 sample inputs recognised correctly; random/non-sign images score < 30 % and are rejected as UNKNOWN.
* On harder synthetic tests (sign small and off-centre, up to 12 degrees tilt) about 75-80 % were correct.
* Because it matches against reference images, it works best when the sign fills most of the photo, is roughly
  upright, and looks like the reference. Real photos taken at angles, with glare or heavy occlusion may fail.
  To improve: add more reference images per sign (real photos named e.g. `stop.jpg` replace the drawn ones).
* The reference images are drawn clip-art style, simplified from Indian/Vienna-convention signs.

## Adding a new sign
Add its image to `reference_images/`, add one row in `knowledge_base_data.py`, run `python seed_db.py`.
