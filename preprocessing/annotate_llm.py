import os
import json
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

BATCH_SIZE = 16  # You can increase if you have more memory
MODEL_NAME = "deepseek-ai/deepseek-llm-7b-chat"  # or use a quantized version for speed

# Load DeepSeek LLM
def load_deepseek_pipeline():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        device_map="auto",
        offload_folder="./offload",
        trust_remote_code=True,
        torch_dtype="auto"
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

# Generate prompt for classification
def generate_prompt(title, comment):
    return f"""Determine if the comment is "Related" or "Not Related" to the post title.

Post Title: {title}
Comment: {comment}
Label:"""

# Parse label from generated output
def extract_label(response_text):
    try:
        label_line = response_text.split("Label:")[-1].strip().lower()
        if "related" in label_line:
            return "Related"
        return "Not Related"
    except Exception:
        return "ERROR"

# Annotate all comments with batching
def annotate_comments(output_path="data/labeled/labeled_comments.json"):
    os.makedirs("data/labeled", exist_ok=True)
    comments = load_all_comments()

    if not comments:
        print("⚠️ No comments found in raw directory.")
        return

    generator = load_deepseek_pipeline()
    labeled = []

    # Process in batches
    for i in tqdm(range(0, len(comments), BATCH_SIZE), desc="Annotating"):
        batch = comments[i:i + BATCH_SIZE]
        prompts = []
        metadata = []

        for comment in batch:
            title = comment.get("post_title") or comment.get("title") or ""
            body = comment.get("body", "")
            if not title or not body:
                continue
            prompts.append(generate_prompt(title, body))
            metadata.append(comment)

        try:
            outputs = generator(prompts, max_new_tokens=10, do_sample=False)
            for out, meta in zip(outputs, metadata):
                result = out['generated_text']
                label = extract_label(result)
                if label != "ERROR":
                    meta["label"] = label
                    labeled.append(meta)
        except Exception as e:
            print(f"Batch error: {e}")
            continue

    with open(output_path, "w") as f:
        json.dump(labeled, f, indent=2)

    print(f"\n✅ Annotated {len(labeled)} comments → saved to: {output_path}")

if __name__ == "__main__":
    annotate_comments()
