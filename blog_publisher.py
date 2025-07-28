import os
import openai
import datetime
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
BLOG_DIR = "/Users/savedis/Documents/TTB-blog/_posts"
TOPICS = [
    ("grants", "Write a 700-750 word blog post about college grants, scholarships, or funding opportunities."),
    ("resume", "Write a 700-750 word blog post with resume writing tips, including formatting, tone, and action verbs."),
    ("essays", "Write a 700-750 word blog post about how to write a strong college admissions essay.")
]

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Generate blog content with OpenAI
def generate_post(prompt):
    print(f"🧠 Generating blog post for topic: {prompt}")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Save content to markdown file with front matter
def save_post(category, content):
    today = datetime.date.today()
    title = content.splitlines()[0].strip()
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
    print("🚀 Running blog automation now...")
    run_blog_automation()
