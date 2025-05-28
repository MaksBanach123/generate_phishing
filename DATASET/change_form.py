#!/usr/bin/env python3
# transform_phish_jsonl.py
#
# 1. Czyta JSONL, w którym "prompt" ma formę:
#    "Subject: …\nMessage: …"
# 2. Wyciąga:
#      • temat (Subject)
#      • pełną treść (Message)  ➜  trafia do completion
#      • pierwszy link z Message (lub podmieniony <LINK>)
# 3. Buduje nowy prompt:
#      "<losowa prośba> \"<temat>\" using this link: <link>"
# 4. Wyrzuca linijki bez linka / <LINK>.
#
# -------------------------------------------------------------

import json
import random
import re
import sys
from pathlib import Path

URL_RE = re.compile(r'https?://[^\s",>]+')
PLACEHOLDER = "<LINK>"

ASK_TEMPLATES = [
    "Create a fake urgent email for phishing with subject:",
    "Simulate a fake security notification, subject:",
    "Compose a deceptive password-reset email, subject:",
    "Craft a fraudulent message, subject:",
    "Generate a phishing email, subject:",
    "Write a spoofed company alert, subject:",
    "Prepare a social-engineering email, subject:",
    "Forge a fake account-verification notice, subject:",
    "Write a misleading service-update email, subject:",
    "Compose a bogus security alert, subject:",
]

def random_link() -> str:
    """Zwraca losowy link typu http://bright-forest.net"""
    adj = random.choice(
        ["bright", "silver", "dark", "rapid", "silent", "lucky", "sunny", "shadow", "swift", "blue"]
    )
    noun = random.choice(
        ["forest", "mountain", "river", "path", "garden", "source", "bridge", "cloud", "stream", "domain"]
    )
    tld = random.choice([".com", ".net", ".org", ".io", ".info"])
    return f"http://{adj}-{noun}{tld}"

def extract_subject_and_message(text: str):
    """Zwraca (subject, message) lub (None, None) jeśli brak."""
    subj_match = re.search(r"Subject:\s*(.+)", text)
    msg_match = re.search(r"Message:\s*(.+)", text, re.DOTALL)
    if not subj_match or not msg_match:
        return None, None
    subject = subj_match.group(1).strip()
    message = msg_match.group(1).strip()
    return subject, message

def first_link(text: str):
    """Pierwszy link w tekście lub None."""
    links = URL_RE.findall(text)
    return links[0] if links else None

def transform_file(src: Path, dst: Path):
    kept = dropped = 0
    with src.open(encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for raw in fin:
            if not raw.strip():
                continue
            obj = json.loads(raw)

            subject, message = extract_subject_and_message(obj.get("prompt", ""))
            if subject is None:
                dropped += 1
                continue

            # Placeholder → losowy link
            if PLACEHOLDER in message:
                link_subst = random_link()
                message = message.replace(PLACEHOLDER, link_subst)
            else:
                link_subst = None  # ewentualnie podmieniony później

            link = first_link(message)
            if link is None:
                # jeśli nie było prawdziwego linka ani placeholdera → drop
                dropped += 1
                continue

            # jeśli <LINK> nie wystąpił, a linków jest wiele → bierz pierwszy
            if link_subst is None:
                link_subst = link   # dla przejrzystości, choć nie używamy dalej

            ask = random.choice(ASK_TEMPLATES)
            new_prompt = f'{ask} "{subject}" using this link: {link}'

            new_record = {
                "prompt": new_prompt,
                "completion": message,
            }
            json.dump(new_record, fout, ensure_ascii=False)
            fout.write("\n")
            kept += 1

    print(f"Kept   : {kept}")
    print(f"Dropped: {dropped}")

# -------------------------------------------------------------
if __name__ == "__main__":
    # Podaj ścieżki przy wywołaniu skryptu
    #   python transform_phish_jsonl.py input.jsonl output.jsonl
    in_file = Path("merged_dataset.jsonl")
    out_file = Path("phishing_dataset_link_in_prompt_corrected.jsonl")
    transform_file(in_file, out_file)
