# reddit_scraper/fetch_comments.py

import praw
import os
import json
from dotenv import load_dotenv

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


def fetch_post_comments(post_id, output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    submission = reddit.submission(id=post_id)
    submission.comments.replace_more(limit=None)

    post_title = submission.title  # ✅ get the title of the post

    def collect_comments(comment_list, parent=None):
        results = []
        for comment in comment_list:
            results.append({
                "id": comment.id,
                "parent_id": parent,
                "body": comment.body,
                "score": comment.score,
                "author": str(comment.author),
                "created_utc": comment.created_utc,
                "permalink": f"https://reddit.com{comment.permalink}",
                "depth": comment.depth,
                "post_title": post_title   # ✅ include post title in each comment
            })
            if hasattr(comment, "replies"):
                results.extend(collect_comments(comment.replies, comment.id))
        return results

    comment_tree = collect_comments(submission.comments)

    with open(os.path.join(output_dir, f"comments_{post_id}.json"), "w") as f:
        json.dump(comment_tree, f, indent=2)

    return len(comment_tree)
