# preprocessing/annotate_llm.py

import os
import json
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


# Load DeepSeek LLM
def load_deepseek_pipeline():
    model_name = "deepseek-ai/deepseek-llm-7b-chat"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",  # auto-load to GPU if available
        trust_remote_code=True,
        torch_dtype="auto"
    )
    return pipeline("text-generation", model=model, tokenizer=tokenizer)


# Load comments from disk
def load_all_comments(raw_dir="data/raw"):
    all_comments = []
    for filename in os.listdir(raw_dir):
        if filename.startswith("comments_") and filename.endswith(".json"):
            with open(os.path.join(raw_dir, filename)) as f:
                all_comments += json.load(f)
    return all_comments


# Classify using DeepSeek
def classify_comment(comment_text, generator):
    prompt = f"""
You are an assistant classifying Reddit comments. Label each comment as either "Informative" or "Not Informative".

Informative comments provide facts, explanations, answers, or helpful advice.
Not Informative comments are jokes, sarcasm, vague, or add no value.

Comment: "{comment_text}"

Label: [Informative / Not Informative]
"""
    try:
        result = generator(prompt, max_new_tokens=20, do_sample=False)[
            0]['generated_text']
        if "Informative" in result and "Not" not in result:
            return "Informative"
        return "Not Informative"
    except Exception as e:
        print(f"Error: {e}")
        return "ERROR"


# Annotate all comments
def annotate_comments(output_path="data/labeled/labeled_comments.json"):
    os.makedirs("data/labeled", exist_ok=True)
    comments = load_all_comments()
    generator = load_deepseek_pipeline()
    labeled = []

    for comment in tqdm(comments, desc="Annotating"):
        label = classify_comment(comment.get("body", ""), generator)
        if label != "ERROR":
            comment["label"] = label
            labeled.append(comment)

    with open(output_path, "w") as f:
        json.dump(labeled, f, indent=2)


if __name__ == "__main__":
    annotate_comments()
