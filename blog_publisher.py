import os
import openai
import datetime
import subprocess
import random
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
BLOG_DIR = "/Users/savedis/Documents/TTB-blog/_posts"
TOPICS = [
    "grants",
    "resume",
    "essays"
]

# Live context function: fetches trending news headlines (simulated fallback)
def get_trending_context():
    try:
        response = requests.get("https://api.thenewsapi.com/v1/news/top?api_token=demo&language=en&limit=5")
        headlines = [item['title'] for item in response.json().get('data', [])]
        return "Trending topics this week: " + "; ".join(headlines)
    except:
        return "Recent FAFSA delays, AI resumes on LinkedIn, and 2025 scholarship application trends."

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Generate blog content with OpenAI using real-world relevance
def generate_post(topic):
    month = datetime.datetime.now().strftime("%B")
    year = datetime.datetime.now().year
    context = get_trending_context()

    prompt = f"""
    You are a blog writer for an education and career consulting company.

    Write a 700–750 word blog post related to the topic: "{topic}". You must make the blog feel highly relevant to {month} {year}.

    Consider any trending news or cultural developments that relate to the topic.
    Use this context to guide your tone and structure: {context}

    Pick an engaging tone (inspiring, urgent, witty, heartfelt, or practical) and a format that suits the week (how-to guide, listicle, myth-busting, case study, etc.).

    Your title must be original, clear, and not reuse past wording. Use compelling headline strategies.

    End the post with a soft, friendly call to action referencing tothroughbeyond.com.
    """

    print(f"🧠 Generating blog post for topic: {topic}")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return response.choices[0].message.content.strip()

# Save content to markdown file with front matter
def save_post(category, content):
    today = datetime.date.today()
    title = content.splitlines()[0].strip("* ")  # Clean title of asterisks or bullets
    slug = title.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("–", "-")
    filename = f"{today.strftime('%Y-%m-%d')}-{slug[:40]}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    with open(filepath, "w") as f:
        f.write(f"---\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"layout: post\n")
        f.write(f"categories: {category}\n")
        f.write(f"---\n\n")
        f.write(content)

    print(f"✅ Blog post saved: {filepath}")
    return filepath

# Commit and push to GitHub
def push_to_github():
    print("📤 Committing and pushing to GitHub...")
    subprocess.run(["git", "pull", "--rebase"], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "add", "."], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "push"], cwd="/Users/savedis/Documents/TTB-blog")
    print("✅ Changes pushed to GitHub!")

# Main automation function
def run_blog_automation():
    topic = get_weekly_topic()
    content = generate_post(topic)
    save_post(topic, content)
    push_to_github()

# Run immediately when script is called
if __name__ == "__main__":
    print("🚀 Running blog automation now...")
    run_blog_automation()
