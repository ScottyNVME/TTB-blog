import os
import openai
import datetime
import subprocess
import re
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
BLOG_DIR = "/Users/savedis/Documents/TTB-blog/_posts"
REPO_DIR = "/Users/savedis/Documents/TTB-blog"
TOPICS = [
    ("grants", "Write a 700-750 word blog post about college grants, scholarships, or funding opportunities."),
    ("resume", "Write a 700-750 word blog post with resume writing tips, including formatting, tone, and action verbs."),
    ("essays", "Write a 700-750 word blog post about how to write a strong college admissions essay.")
]

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Generate blog content using OpenAI
def generate_post(prompt):
    print(f"🧠 Generating blog post for prompt: {prompt}")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Save content to markdown file with Jekyll front matter
def save_post(category, content):
    today = datetime.date.today()
    title = content.splitlines()[0].strip()
    
    # Clean slug: lowercase, hyphenated, no symbols
    raw_slug = title.lower().replace(" ", "-").replace("–", "-")
    clean_slug = re.sub(r"[^a-z0-9\-]", "", raw_slug)[:40]  # limit filename length

    filename = f"{today.strftime('%Y-%m-%d')}-{clean_slug}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    # Ensure _posts folder exists
    os.makedirs(BLOG_DIR, exist_ok=True)

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
    try:
        subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd=REPO_DIR, check=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", "main"], cwd=REPO_DIR, check=True)
        print("✅ Changes pushed to GitHub!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")

# Main execution
def run_blog_automation():
    category, prompt = get_weekly_topic()
    content = generate_post(prompt)
    save_post(category, content)
    push_to_github()

# Run it immediately
if __name__ == "__main__":
    print("🚀 Running blog automation now...")
    run_blog_automation()

