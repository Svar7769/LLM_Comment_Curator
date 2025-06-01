# preprocessing/build_tree.py

import json
import os
from collections import defaultdict


def load_labeled_comments(path="data/labeled/labeled_comments.json"):
    with open(path) as f:
        return json.load(f)


def build_thread_tree(comments):
    comment_map = {c["id"]: c for c in comments}
    tree = defaultdict(list)

    for c in comments:
        parent_id = c.get("parent_id")
        if parent_id and parent_id in comment_map:
            tree[parent_id].append(c)
        else:
            tree[None].append(c)  # root-level comment

    def attach_children(comment):
        comment["children"] = [attach_children(
            child) for child in tree.get(comment["id"], [])]
        return comment

    return [attach_children(root) for root in tree[None]]


def build_all_trees(output_path="data/processed/thread_trees.json"):
    comments = load_labeled_comments()
    trees = build_thread_tree(comments)
    os.makedirs("data/processed", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(trees, f, indent=2)


if __name__ == "__main__":
    build_all_trees()
