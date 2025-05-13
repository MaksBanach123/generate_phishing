import pandas as pd
import json

def csv_to_prompt_completion(input_csv_path, output_jsonl_path):
    
    df = pd.read_csv(
        input_csv_path,
        sep=",",
        quotechar='"',
        escapechar="\\",
        engine="python",
        encoding="utf-8",
        on_bad_lines='skip'
    )

    print

    df = df[df['body'].notnull() & df['subject'].notnull()]

    with open(output_jsonl_path, "w", encoding="utf-8") as f:
        for _, row in df.iterrows():
            subject = row['subject']
            body = row['body'].strip().replace('\n', ' ')
            prompt = f"Subject: {subject}\n\nEmail body: {body}"
            completion = ""
            json_line = {"prompt": prompt, "completion": completion}
            f.write(json.dumps(json_line, ensure_ascii=False) + "\n")


csv_to_prompt_completion("Nazario.csv", "dataset_prompt_completion.jsonl")


