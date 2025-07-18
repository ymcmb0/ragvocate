import pdfplumber
import re
import os
import json
from dotenv import load_dotenv
load_dotenv()
# === File and Output Path ===
pdf_path = os.getenv("PDF_PATH")
output_dir = os.getenv("STATUTES_RAW_TEXT")
output_dir_md = os.getenv("STATUTES_RAW_META")
os.makedirs(output_dir, exist_ok=True)

# === Regex for detecting section starts and notes ===
section_start_re = re.compile(r"^§\s?(\d{3,4}[a-zA-Z\-]*)\.\s+(.+)$")
subchapter_re = re.compile(r"^SUBCHAPTER\s+([IVXLC]+)—(.+)$", re.I)
part_re = re.compile(r"^PART\s+([IVXLC]+)—(.+)$", re.I)

note_starts = {
    "amendments": re.compile(r"^AMENDMENTS$", re.I),
    "effective_date": re.compile(r"^EFFECTIVE DATE(?: OF [A-Z0-9 ,\(\)\-]+)?$", re.I),
    "references": re.compile(r"^REFERENCES IN TEXT$", re.I),
    "abolition": re.compile(r"^ABOLITION OF IMMIGRATION.*$", re.I),
    "notes": re.compile(r"^\[?NOTES\]?$", re.I),
    "statutory_notes": re.compile(r"^STATUTORY NOTES.*$", re.I),
    "editorial_notes": re.compile(r"^EDITORIAL NOTES.*$", re.I),
}

# === Helper: Save each section as txt + metadata ===
def save_section(sec):
    if not sec or not sec.get("section"):
        return
    base_name = re.sub(r"[^\w\-]", "_", sec["section"])
    with open(os.path.join(output_dir, f"{base_name}.txt"), "w", encoding="utf-8") as f:
        f.write(f"Title: {sec['title']}\n")
        f.write(f"Chapter: {sec['chapter']}\n")
        f.write(f"Subchapter: {sec.get('subchapter', 'N/A')}\n")
        f.write(f"Part: {sec.get('part', 'N/A')}\n")
        f.write(f"Section: {sec['section']} - {sec['section_title']}\n")
        f.write(f"Source: {sec['source']}\n\n")
        for part in ["main_text", "amendments", "effective_date", "references", "notes", "statutory_notes", "editorial_notes"]:
            content = sec.get(part, "").strip()
            if content:
                f.write(f"[{part.upper().replace('_', ' ')}]\n{content}\n\n")
    with open(os.path.join(output_dir_md, f"{base_name}_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(sec, f, indent=2)

# === Extract all text from left/right columns ===
all_lines = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        width = page.width
        left_bbox = (0, 0, width / 2, page.height)
        right_bbox = (width / 2, 0, width, page.height)

        left_text = page.within_bbox(left_bbox).extract_text() or ""
        right_text = page.within_bbox(right_bbox).extract_text() or ""

        lines = (left_text + "\n" + right_text).split("\n")

        # Fix wrapped words and remove noise
        fixed_lines = []
        buffer = ""
        for line in lines:
            line = line.strip()
            line = re.sub(r"([a-z])([A-Z])", r"\1 \2", line)
            if re.match(r"^(ND )?NATIONALITY( Page \d+)?$|^Page \d+ TITLE 8.*$|^§\d+[a-zA-Z\-]* TITLE 8.*$", line):
                continue
            if buffer:
                if line and not line[0].islower():
                    fixed_lines.append(buffer)
                    buffer = line
                else:
                    buffer = buffer.rstrip("-") + line
            else:
                buffer = line
        if buffer:
            fixed_lines.append(buffer)
        all_lines.extend(fixed_lines)

# === Parse extracted lines ===
current_section = None
current_part = "main_text"
current_subchapter = ""
current_part_title = ""

for line in all_lines:
    line = line.strip()

    # Detect subchapter or part
    sub_match = subchapter_re.match(line)
    if sub_match:
        current_subchapter = f"SUBCHAPTER {sub_match.group(1)} — {sub_match.group(2).strip()}"
        continue
    part_match = part_re.match(line)
    if part_match:
        current_part_title = f"PART {part_match.group(1)} — {part_match.group(2).strip()}"
        continue

    # Start of a new section
    match = section_start_re.match(line)
    if match:
        save_section(current_section)
        current_section = {
            "title": "Title 8 - Aliens and Nationality",
            "chapter": "Chapter 12 - Immigration and Nationality",
            "subchapter": current_subchapter,
            "part": current_part_title,
            "section": f"§{match.group(1)}",
            "section_title": match.group(2),
            "source": "USCODE-2023-title8.pdf",
            "main_text": "",
            "amendments": "",
            "effective_date": "",
            "references": "",
            "notes": "",
            "statutory_notes": "",
            "editorial_notes": ""
        }
        current_part = "main_text"
        continue

    # Check for part change (e.g. AMENDMENTS, NOTES, etc.)
    for part_key, pattern in note_starts.items():
        if pattern.match(line):
            current_part = part_key
            break
    else:
        if current_section:
            current_section[current_part] += line + "\n"

# Save last section
save_section(current_section)

print("✅ All done. Subchapter and Part tracking added.\n📂 Check folder:", output_dir)
