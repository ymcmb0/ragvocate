import glob
import json
import os

from dotenv import load_dotenv

load_dotenv()
# === Settings ===
input_text_dir = os.getenv("PRECEDENTS_RAW_TEXT")
input_metadata_dir = os.getenv("PRECEDENTS_RAW_META")
output_jsonl_path = os.getenv("PRECEDENTS_PROCESSED_TEXT")
chunk_size = 500
overlap = 100

# === Ensure output directory exists ===
os.makedirs(os.path.dirname(output_jsonl_path), exist_ok=True)

# === Collect all txt files ===
txt_files = glob.glob(os.path.join(input_text_dir, "*.txt"))


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
        metadata_path = os.path.join(input_metadata_dir, f"{base_name}_metadata.json")

        if not os.path.exists(metadata_path):
            print(f"Metadata missing for {base_name}")
            continue

        # Read full text
        with open(txt_path, "r", encoding="utf-8") as f:
            full_text = f.read().strip()

        # Read metadata
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        # Split into chunks
        chunks = chunk_text(full_text, chunk_size, overlap)

        # Write each chunk
        for idx, chunk in enumerate(chunks):
            entry = {
                "id": f"{base_name}_chunk_{idx+1}",
                "text": chunk.strip(),
                "metadata": metadata,
            }
            out_file.write(json.dumps(entry) + "\n")

print("All precedent files chunked and written to JSONL:")
print("", output_jsonl_path)
