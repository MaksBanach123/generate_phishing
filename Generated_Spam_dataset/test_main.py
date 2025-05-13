import pandas as pd
import json
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType

def tokenize_function(example):
    inputs = tokenizer(example["prompt"], truncation=True, padding="max_length")
    inputs["labels"] = inputs["input_ids"]
    return inputs

df = pd.read_csv("TD_Spam_Generated_300.csv", sep="\t", encoding="latin1")
print(df.columns)
prompts = []

for idx, row in df.iterrows():
    prompt_text = f"Subject: {row['Title']}\nMessage: {row['Text']}"
    prompts.append(prompt_text)

with open("data_prompts.jsonl", "w", encoding="utf-8") as outfile:
    for prompt_text in prompts:
        entry = {"prompt": prompt_text, "completion": ""}  # brak rzeczywistej odpowiedzi
        outfile.write(json.dumps(entry, ensure_ascii=False) + "\n")


dataset = load_dataset("json", data_files={"train": "data_prompts.jsonl"}, split="train")
model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05
)

model = get_peft_model(model, peft_config)
train_dataset = dataset

train_dataset = train_dataset.map(tokenize_function, batched=True)
train_dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

training_args = TrainingArguments(
    output_dir="output",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    save_steps=100,
    logging_steps=50
)
trainer = Trainer(model=model, args=training_args, train_dataset=train_dataset)
trainer.train()
