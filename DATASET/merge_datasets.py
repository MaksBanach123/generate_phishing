import glob
import os

# Lista folderów z datasetami
folders = ["CEAS_DATASET", "Generated_Spam_dataset", "NAZARIO DATASET"]

# Plik wyjściowy
output_file = "merged_dataset.jsonl"

# Otwórz plik wyjściowy
with open(output_file, "w", encoding="utf-8") as outfile:
    total_files = 0
    total_lines = 0

    for folder in folders:
        jsonl_files = glob.glob(os.path.join(folder, "*.jsonl"))
        for file in jsonl_files:
            total_files += 1
            with open(file, "r", encoding="utf-8") as infile:
                for line in infile:
                    line = line.strip()
                    if line:
                        outfile.write(line + "\n")
                        total_lines += 1

print(f"✅ Zmergowano {total_files} plików z {len(folders)} folderów.")
print(f"🔢 Łącznie zapisano {total_lines} przykładów do {output_file}")
