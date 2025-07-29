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
    (
        "grants",
        "Write a fresh and engaging 700-750 word blog post about college grants or funding opportunities. "
        "Include the latest government or private funding trends (as of this week), unique or overlooked scholarships, "
        "and how students can position themselves to win. End with a subtle call to explore free college guidance at tothroughbeyond.com."
    ),
    (
        "resume",
        "Write a timely and original 700-750 word blog post with advanced resume tips for students or recent grads in today's job market. "
        "Include current hiring trends, AI resume screening tips, and bold action verbs. Make sure it sounds unique and not similar to previous posts. "
        "Finish by encouraging readers to explore free tools and advice at tothroughbeyond.com."
    ),
    (
        "essays",
        "Write a compelling 700-750 word blog post on how to write a standout college admissions essay in 2025. "
        "Use recent trends in what admissions officers are looking for (tone, storytelling, authenticity). Provide concrete examples and strategies. "
        "Conclude with a subtle nudge toward free essay guidance at tothroughbeyond.com."
    )
]

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Generate blog content with OpenAI
def generate_post(prompt):
    print(f"🧠 Generating blog post for prompt: {prompt}")
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
    repo_path = "/Users/savedis/Documents/TTB-blog"
    subprocess.run(["git", "add", "."], cwd=repo_path)
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd=repo_path)
    subprocess.run(["git", "push", "--set-upstream", "origin", "main"], cwd=repo_path)
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


