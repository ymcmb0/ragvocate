import os
import re
import json
from dotenv import load_dotenv
load_dotenv()
# === CONFIG ===
precedents_dir =os.getenv("PRECEDENTS_RAW_TEXT")
output_dir = os.getenv("PRECEDENTS_RAW_META")
os.makedirs(output_dir, exist_ok=True)

# === Patterns ===
case_id_pattern = re.compile(r"^(.*?)\s+\((\d{4})\)")
law_ref_pattern = re.compile(r"\bsection\s+(\d+[a-zA-Z0-9()\-]*)", re.IGNORECASE)
const_ref_pattern = re.compile(r"\b(?:First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Fourteenth)\s+Amendment", re.IGNORECASE)

# === Main Loop ===
for fname in os.listdir(precedents_dir):
    if not fname.endswith(".txt"):
        continue

    filepath = os.path.join(precedents_dir, fname)
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().strip()

    lines = text.splitlines()
    first_line = lines[0] if lines else ""
    body_text = "\n".join(lines[1:]).strip()

    # Extract case ID and year
    case_id = "Unknown"
    year = "Unknown"
    m = case_id_pattern.match(first_line)
    if m:
        case_id = m.group(1).strip()
        year = m.group(2).strip()

    # Extract summary (first paragraph or first 2-3 sentences)
    summary = ""
    summary_lines = body_text.split("\n")
    for line in summary_lines:
        if len(line.strip()) > 50:
            summary = line.strip()
            break

    # Extract law references and constitutional references
    laws = list(set(law_ref_pattern.findall(body_text)))
    consts = list(set(const_ref_pattern.findall(body_text)))

    # Metadata JSON
    metadata = {
        "case_id": case_id,
        "source": "precedents",
        "title": first_line.strip() if first_line else "Unknown Title",
        "year": year,
        "summary": summary,
        "law_referenced": laws,
        "constitution_referenced": consts
    }

    # Save .json
    output_path = os.path.join(output_dir, fname.replace(".txt", "_metadata.json"))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Created metadata for: {fname}")

print("\nDone generating metadata!")
print("\nOutput folder:", output_dir)
