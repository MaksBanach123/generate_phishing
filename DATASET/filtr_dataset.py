import pandas as pd

# Wczytaj plik JSONL do DataFrame
df = pd.read_json("merged_dataset.jsonl", lines=True)

# Sprawdź liczbę wierszy przed
print(f"🔢 Przed usunięciem duplikatów: {len(df)} przykładów")

# Usuń duplikaty (identyczne wiersze)
df_cleaned = df.drop_duplicates()

# Połącz prompt i completion w jedno pole 'text'
df_cleaned["text"] = df_cleaned["prompt"].str.strip() + "\n" + df_cleaned["completion"].str.strip()

# Usuń puste (np. brak completion lub prompt po czyszczeniu)
df = df_cleaned[df_cleaned["text"].str.strip() != ""]

# Wybierz tylko kolumnę 'text'
df_final = df[["text"]]

# Zapisz do nowego pliku JSONL
df_final.to_json("dataset_text_version.jsonl", orient="records", lines=True, force_ascii=False)

print(f"✅ Gotowe! Zapisano {len(df_final)} rekordów do dataset_text_version.jsonl")