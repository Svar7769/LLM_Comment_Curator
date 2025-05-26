from reddit_scraper.fetch_posts import fetch_topic_posts
from reddit_scraper.fetch_comments import fetch_post_comments

topics = ["India Pakistan war"]
for topic in topics:
    print(f"🔍 Scraping posts for topic: {topic}")
    post_ids = fetch_topic_posts(topic, limit=100)
    for pid in post_ids:
        print(f"💬 Fetching comments for post: {pid}")
        fetch_post_comments(pid)