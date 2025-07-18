import os
import json
import glob
from dotenv import load_dotenv
load_dotenv()
# === Settings ===
text_dir = os.getenv("STATUTES_RAW_TEXT")
metadata_dir = os.getenv("STATUTES_RAW_META")
output_path= os.getenv("STATUTES_PROCESSED_TEXT")
output_jsonl_path = os.path.join(output_path, "statutes_chunks.jsonl")
chunk_size = 500
overlap = 100

# === Ensure output directory exists ===
os.makedirs(os.path.dirname(output_jsonl_path), exist_ok=True)

# === Collect all text files (skip metadata files) ===
txt_files = glob.glob(os.path.join(text_dir, "*.txt"))

# === Chunking Function ===
def chunk_text(text, size, overlap):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

# === Process Files ===
with open(output_jsonl_path, "w", encoding="utf-8") as out_file:
    for txt_path in txt_files:
        base_name = os.path.basename(txt_path).replace(".txt", "")
        metadata_path = os.path.join(metadata_dir, f"{base_name}_metadata.json")

        if not os.path.exists(metadata_path):
            print(f"Metadata missing for {base_name}")
            continue

        # Read text
        with open(txt_path, "r", encoding="utf-8") as f:
            full_text = f.read().strip()

        # Read metadata
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Chunk text
        chunks = chunk_text(full_text, chunk_size, overlap)

        # Write each chunk
        for idx, chunk in enumerate(chunks):
            entry = {
                "id": f"{metadata['section']}_chunk_{idx+1}",
                "text": chunk,
                "metadata": metadata
            }
            out_file.write(json.dumps(entry) + "\n")

print("All statute chunks written to JSONL:")
print("", output_jsonl_path)
