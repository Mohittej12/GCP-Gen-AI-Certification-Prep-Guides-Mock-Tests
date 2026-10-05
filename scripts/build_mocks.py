"""
Build data/mocks.json with 50 questions and 90 min per test.
Section weights: 30/35/20/15. Existing Mock 1-7 are preserved.
"""
import json
import os
import random
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(APP_ROOT, "data")
QUESTIONS_PATH = os.path.join(DATA_DIR, "questions.json")
MOCKS_PATH = os.path.join(DATA_DIR, "mocks.json")

# Exam section weights: 1=30%, 2=35%, 3=20%, 4=15%
SECTION_WEIGHTS = {1: 0.30, 2: 0.35, 3: 0.20, 4: 0.15}
QUESTIONS_PER_MOCK = 50
DURATION_MINUTES = 90


def main():
    with open(QUESTIONS_PATH, "r", encoding="utf-8") as f:
        questions = json.load(f)
    by_section = {1: [], 2: [], 3: [], 4: []}
    seen_question_texts = set()
    for q in questions:
        s = q.get("section", 1)
        if s not in by_section:
            continue
        normalized_text = re.sub(r"[^a-z0-9]+", " ", q.get("questionText", "").casefold()).strip()
        if not normalized_text or normalized_text in seen_question_texts:
            continue
        seen_question_texts.add(normalized_text)
        by_section[s].append(q["id"])

    num_mocks = 12
    existing_mocks = []
    if os.path.isfile(MOCKS_PATH):
        with open(MOCKS_PATH, "r", encoding="utf-8") as f:
            existing_mocks = json.load(f)
    existing_by_id = {mock["mockId"]: mock for mock in existing_mocks}
    mocks = []
    rng = random.Random(42)  # reproducible
    for i in range(1, num_mocks + 1):
        n = QUESTIONS_PER_MOCK
        n1 = max(1, round(n * SECTION_WEIGHTS[1]))
        n2 = max(1, round(n * SECTION_WEIGHTS[2]))
        n3 = max(1, round(n * SECTION_WEIGHTS[3]))
        n4 = n - n1 - n2 - n3
        if n4 < 1:
            n4 = 1
            n1 = n - n2 - n3 - n4
        ids1 = rng.sample(by_section[1], min(n1, len(by_section[1])))
        ids2 = rng.sample(by_section[2], min(n2, len(by_section[2])))
        ids3 = rng.sample(by_section[3], min(n3, len(by_section[3])))
        ids4 = rng.sample(by_section[4], min(n4, len(by_section[4])))
        all_ids = ids1 + ids2 + ids3 + ids4
        rng.shuffle(all_ids)
        mock = {
            "mockId": f"mock-{i}",
            "title": f"Mock {i}",
            "subtitle": "Additional practice from Sets 1-5" if i > 7 else "Mixed-topic practice",
            "questionCount": len(all_ids),
            "durationMinutes": DURATION_MINUTES,
            "questionIds": all_ids,
        }
        if i <= 7 and mock["mockId"] in existing_by_id:
            mocks.append(existing_by_id[mock["mockId"]])
        else:
            mocks.append(mock)
    generated_ids = {mock["mockId"] for mock in mocks}
    mocks.extend(mock for mock in existing_mocks if mock["mockId"] not in generated_ids)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MOCKS_PATH, "w", encoding="utf-8") as f:
        json.dump(mocks, f, indent=2)
    print(f"Wrote {len(mocks)} mocks to {MOCKS_PATH}")


if __name__ == "__main__":
    main()
