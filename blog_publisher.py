import os
import openai
import datetime
import subprocess
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
BLOG_DIR = "/Users/savedis/Documents/TTB-blog/_posts"
TOPICS = [
    ("grants", "Generate a timely 700–750 word blog post covering recent trends, news, or opportunities related to college grants, scholarships, or alternative funding methods. Make it informative, engaging, and SEO-friendly. Include real-world programs, stats, or deadlines mentioned in recent updates."),
    ("resume", "Write a fresh 700–750 word blog post on resume writing that reflects new hiring trends or job market shifts. Reference current formatting expectations, action verbs, or examples used in recent top-tier resumes. Make it engaging, original, and practical for job seekers."),
    ("essays", "Generate an engaging and insightful 700–750 word blog post on writing a powerful college admissions essay, highlighting new themes, recent trends, or techniques that have emerged. Use examples and offer clear guidance that sets this post apart from previous ones.")
]

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Generate blog content with OpenAI
def generate_post(prompt):
    print(f"\U0001F9E0 Generating blog post for prompt: {prompt}")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Convert title to title case and clean it up for display and file naming
def clean_title(raw_title):
    title = raw_title.replace("**", "").strip()
    title = re.sub(r'[^\w\s-]', '', title)  # Remove special chars
    title = title.title()  # Title Case
    return title

# Save content to markdown file with front matter
def save_post(category, content):
    today = datetime.date.today()
    raw_title = content.splitlines()[0].strip()
    title = clean_title(raw_title)
    slug = title.lower().replace(" ", "-")[:40]
    filename = f"{today.strftime('%Y-%m-%d')}-{slug}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    # Build full markdown with subtitle and emoji
    body = "\n".join(content.splitlines()[1:]).strip()
    formatted = f"---\n"
    formatted += f"title: \"{title}\"\n"
    formatted += f"layout: post\n"
    formatted += f"categories: {category}\n"
    formatted += f"---\n\n"
    formatted += f"✍️ _Published on {today.strftime('%B %d, %Y')}_\n\n"
    formatted += f"## {title}\n\n"
    formatted += f"{body}\n"

    with open(filepath, "w") as f:
        f.write(formatted)

    print(f"✅ Blog post saved: {filepath}")
    return filepath

# Commit and push to GitHub
def push_to_github():
    print("\U0001F4E4 Committing and pushing to GitHub...")
    subprocess.run(["git", "add", "."], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "push"], cwd="/Users/savedis/Documents/TTB-blog")
    print("✅ Changes pushed to GitHub!")

# Main automation function
def run_blog_automation():
    category, prompt = get_weekly_topic()
    content = generate_post(prompt)
    save_post(category, content)
    push_to_github()

# Run immediately when script is called
if __name__ == "__main__":
    print("\U0001F680 Running blog automation now...")
    run_blog_automation()
