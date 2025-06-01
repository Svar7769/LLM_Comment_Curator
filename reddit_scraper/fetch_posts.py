# reddit_scraper/fetch_posts.py

import praw
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  # Load Reddit credentials from .env file

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)


def fetch_topic_posts(topic, limit=1000, subreddit="all", output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    results = []

    for submission in reddit.subreddit(subreddit).search(topic, limit=limit, sort='new'):
        results.append({
            "topic": topic,
            "title": submission.title,
            "selftext": submission.selftext,
            "score": submission.score,
            "num_comments": submission.num_comments,
            "upvote_ratio": submission.upvote_ratio,
            "created_utc": submission.created_utc,
            "created_time": datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "author": str(submission.author),
            "subreddit": submission.subreddit.display_name,
            "url": submission.url,
            "permalink": f"https://www.reddit.com{submission.permalink}",
            "id": submission.id,
            "is_self": submission.is_self,
            "over_18": submission.over_18,
            "domain": submission.domain,
            "removed_by_category": submission.removed_by_category,
            "link_flair_text": submission.link_flair_text
        })

    # Save results
    output_path = os.path.join(
        output_dir, f"posts_{topic.replace(' ', '_')}.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    return [post["id"] for post in results]  # return post IDs
