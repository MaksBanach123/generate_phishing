import re
import json
import pandas as pd
from pathlib import Path

###############################################################################
# 1. Wczytanie surowego CSV (39154 wierszy, 7 kolumn)
###############################################################################
df = pd.read_csv(
    "CEAS_08.csv",
    encoding="utf-8",
    delimiter=",",
    quotechar='"',
    low_memory=False,
)

###############################################################################
# 2. Delikatne oczyszczenie treści – zamiana \n na realne nowe linie + usunięcie ">"
###############################################################################
def normalise(txt: str) -> str:
    if pd.isna(txt):
        return ""
    txt = txt.encode("utf-8").decode("unicode_escape", errors="ignore")
    txt = re.sub(r"^[> ]+", "", txt, flags=re.MULTILINE)
    txt = re.sub(r"\s+\n", "\n", txt)
    txt = txt.replace('+=', '')
    txt = txt.replace('---', '')
    txt = txt.replace('===', '')
    return txt.strip()

df["subject_clean"] = df["subject"].map(normalise)
df["body_clean"]    = df["body"].map(normalise)

###############################################################################
# 3. Zachowujemy TYLKO spam/phishing (label == 1)
###############################################################################
spam_df = df[df["label"] == 1].copy()

###############################################################################
# 4. Budujemy pole "prompt" w żądanym formacie
###############################################################################
spam_df["prompt"] = (
    "Subject: "
    + spam_df["subject_clean"].fillna("")
    + "\nMessage: "
    + spam_df["body_clean"].fillna("")
)

###############################################################################
# 5. Eksport do pliku JSONL
###############################################################################
out_path = Path("ceas08_spam_prompts.jsonl")
with out_path.open("w", encoding="utf-8") as fp:
    for prompt in spam_df["prompt"]:
        entry = {"prompt": prompt, "completion": ""}
        fp.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"✓ Zapisano {len(spam_df):,} rekordów do {out_path}")
