import re
import os
import json
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm

IMG_REGEX = r"(https?://i\.imgur\.com/\S+\.(?:jpg|png|jpeg|gif))"

def extract_image_urls(text):
    return re.findall(IMG_REGEX, text or "")

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.thumbnail((256, 256))
        img.save(save_path)
        return True
    except Exception:
        return False

def process_images(input_path="data/processed/pruned_trees.json", output_path="data/processed/with_images.json", image_dir="images"):
    os.makedirs(image_dir, exist_ok=True)
    
    with open(input_path) as f:
        trees = json.load(f)

    for tree in tqdm(trees, desc="Processing trees"):
        _attach_images_to_comment(tree, image_dir)

    with open(output_path, "w") as f:
        json.dump(trees, f, indent=2)

def _attach_images_to_comment(comment, image_dir):
    comment_id = comment["id"]
    text = comment.get("body", "") + " " + comment.get("url", "")
    urls = extract_image_urls(text)
    
    comment["images"] = []
    for i, url in enumerate(urls):
        save_path = os.path.join(image_dir, f"{comment_id}_{i}.png")
        if download_image(url, save_path):
            comment["images"].append(save_path)

    for child in comment.get("children", []):
        _attach_images_to_comment(child, image_dir)

if __name__ == "__main__":
    process_images()
