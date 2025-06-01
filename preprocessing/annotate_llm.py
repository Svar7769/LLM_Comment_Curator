# preprocessing/annotate_llm.py

import os
import json
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

# ✅ Define your model name here
MODEL_NAME = "deepseek-ai/deepseek-llm-7b-chat"

# Load DeepSeek LLM using first 3 GPUs


def load_deepseek_pipeline():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="sequential",         # Automatically fills multiple GPUs in order
        offload_folder="./offload",
        trust_remote_code=True,
        torch_dtype=torch.float16
    )

    return pipeline("text-generation", model=model, tokenizer=tokenizer)


# Load all comment files
def load_all_comments(raw_dir="data/raw"):
    all_comments = []
    for filename in os.listdir(raw_dir):
        if filename.startswith("comments_") and filename.endswith(".json"):
            with open(os.path.join(raw_dir, filename)) as f:
                all_comments += json.load(f)
    return all_comments


# Prompt LLM to classify comment
def classify_comment(title, comment_text, generator):
    prompt = f"""
You are an assistant classifying Reddit comments. Determine whether a comment is "Informative" or "Not Informative" **with respect to the original post title**.

- Informative comments contain factual information, useful advice, clarifications, or evidence-based discussion that directly relate to the post title.
- Not Informative comments are vague, emotional, jokes, off-topic, or add no value to the conversation.

Post Title: "{title}"
Comment: "{comment_text}"

Label:"""

    try:
        result = generator(prompt, max_new_tokens=10, do_sample=False)[
            0]['generated_text']
        label_response = result.split("Label:")[-1].strip().split()[0]
        if label_response.lower().startswith("informative"):
            return "Informative"
        return "Not Informative"
    except Exception as e:
        print(f"Error: {e}")
        return "ERROR"


# Annotate all comments
def annotate_comments(output_path="data/labeled/labeled_comments.json"):
    os.makedirs("data/labeled", exist_ok=True)
    comments = load_all_comments()

    if not comments:
        print("⚠️ No comments found in raw directory.")
        return

    generator = load_deepseek_pipeline()
    labeled = []

    for comment in tqdm(comments, desc="Annotating"):
        title = comment.get("post_title") or comment.get("title") or ""
        body = comment.get("body", "")
        if not title or not body:
            continue

        label = classify_comment(title, body, generator)
        if label != "ERROR":
            comment["label"] = label
            labeled.append(comment)

    with open(output_path, "w") as f:
        json.dump(labeled, f, indent=2)

    print(f"\n✅ Annotated {len(labeled)} comments → saved to: {output_path}")


if __name__ == "__main__":
    annotate_comments()
