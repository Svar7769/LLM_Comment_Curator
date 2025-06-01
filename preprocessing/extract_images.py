import re
import os
import json
import requests
from PIL import Image
from io import BytesIO
from tqdm import tqdm

# General image URL regex
IMG_REGEX = r"(https?://[^\s]+?\.(?:jpg|png|jpeg|gif))"

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

def process_images(input_path="data/processed/pruned_trees.json", 
                   output_path="data/processed/with_images.json", 
                   image_dir="images"):
    os.makedirs(image_dir, exist_ok=True)
    
    with open(input_path) as f:
        trees = json.load(f)

    for tree in tqdm(trees, desc="Processing trees"):
        root_images = _attach_images_to_comment(tree, image_dir)
        # Propagate root images if children have no images
        _propagate_images(tree, root_images)

    with open(output_path, "w") as f:
        json.dump(trees, f, indent=2)

def _attach_images_to_comment(comment, image_dir):
    comment_id = comment["id"]
    text = " ".join([
        comment.get("body", ""),
        comment.get("url", ""),
        comment.get("permalink", "")
    ])

    urls = extract_image_urls(text)
    comment["images"] = []

    for i, url in enumerate(urls):
        save_path = os.path.join(image_dir, f"{comment_id}_{i}.png")
        if download_image(url, save_path):
            comment["images"].append(save_path)

    for child in comment.get("children", []):
        _attach_images_to_comment(child, image_dir)

    return comment["images"]

def _propagate_images(comment, inherited_images):
    if not comment.get("images"):
        comment["images"] = inherited_images

    for child in comment.get("children", []):
        _propagate_images(child, comment["images"])

if __name__ == "__main__":
    process_images()
