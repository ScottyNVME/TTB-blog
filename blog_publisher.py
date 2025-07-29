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
    ("grants", "Write a 700–750 word blog post about college grants, scholarships, or funding opportunities."),
    ("resume", "Write a fresh 700–750 word blog post on resume writing that reflects new hiring trends or job market shifts. Reference current formatting expectations, action verbs, or examples used in recent top-tier resumes. Make it engaging, original, and practical for job seekers."),
    ("essays", "Write a 700–750 word blog post about how to write a strong college admissions essay. Include updated advice relevant to the current admissions landscape and highlight fresh tips and common pitfalls to avoid.")
]

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Generate blog content with OpenAI, including current year/month and trending keywords
def generate_post(prompt):
    current_date = datetime.datetime.now().strftime("%B %Y")
    enriched_prompt = (
        f"{prompt} Ensure that the advice is timely and relevant for {current_date}, "
        f"and incorporates or is inspired by currently trending keywords in the topic. "
        f"Add a short call to action encouraging readers to learn more at tothroughbeyond.com."
    )
    print(f"🧠 Generating blog post for prompt: {enriched_prompt}")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": enriched_prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Save content to markdown file with front matter
def save_post(category, content):
    today = datetime.date.today()
    title_line = content.splitlines()[0].strip(" *#")
    slug = title_line.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("–", "-")
    filename = f"{today.strftime('%Y-%m-%d')}-{slug[:40]}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    with open(filepath, "w") as f:
        f.write(f"---\n")
        f.write(f"title: \"{title_line}\"\n")
        f.write(f"layout: post\n")
        f.write(f"categories: {category}\n")
        f.write(f"---\n\n")
        f.write(content)

    print(f"✅ Blog post saved: {filepath}")
    return filepath

# Commit and push to GitHub with upstream tracking
def push_to_github():
    print("📤 Committing and pushing to GitHub...")
    repo_path = "/Users/savedis/Documents/TTB-blog"
    subprocess.run(["git", "pull", "--rebase"], cwd=repo_path)
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
