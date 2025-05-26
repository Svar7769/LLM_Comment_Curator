# preprocessing/export_dataset.py

import json
import pandas as pd
import os


def flatten_comment_tree(comment, thread_id, context=[]):
    row = {
        "id": comment["id"],
        "link_id": thread_id,
        "text": comment["body"],
        "label": comment["label"],
        "context": [c["body"] for c in context[-3:]]  # up to 3 parents
    }
    rows = [row]
    for child in comment.get("children", []):
        rows.extend(flatten_comment_tree(
            child, thread_id, context + [comment]))
    return rows


def export_final_dataset(input_path="data/processed/pruned_trees.json", output_path="data/processed/informative_dataset.parquet"):
    with open(input_path) as f:
        trees = json.load(f)

    all_rows = []
    for tree in trees:
        thread_id = tree["parent_id"] or tree["id"]
        all_rows.extend(flatten_comment_tree(tree, thread_id))

    df = pd.DataFrame(all_rows)
    df.to_parquet(output_path, index=False)
    print(f"✅ Saved dataset to {output_path}")


if __name__ == "__main__":
    export_final_dataset()
