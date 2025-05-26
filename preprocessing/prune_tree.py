# preprocessing/prune_tree.py

import json
import os

MAX_DEPTH = 5


def prune_comment_tree(comment, depth=0):
    if depth >= MAX_DEPTH:
        comment["children"] = []
        return comment
    comment["children"] = [prune_comment_tree(
        child, depth + 1) for child in comment.get("children", [])]
    return comment


def prune_all_trees(input_path="data/processed/thread_trees.json", output_path="data/processed/pruned_trees.json"):
    with open(input_path) as f:
        trees = json.load(f)
    pruned = [prune_comment_tree(tree) for tree in trees]
    with open(output_path, "w") as f:
        json.dump(pruned, f, indent=2)


if __name__ == "__main__":
    prune_all_trees()
