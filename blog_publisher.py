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
TOPIC_INDEX_FILE = "/Users/savedis/Documents/TTB-blog/topic_index.txt"
TOPICS = [
    ("grants", "Write a 700–750 word blog post about college grants, scholarships, or funding opportunities."),
    ("resume", "Write a fresh 700–750 word blog post on resume writing that reflects new hiring trends or job market shifts. Reference current formatting expectations, action verbs, or examples used in recent top-tier resumes. Make it engaging, original, and practical for job seekers."),
    ("essays", "Write a 700–750 word blog post about how to write a strong college admissions essay. Include updated advice relevant to the current admissions landscape and highlight fresh tips and common pitfalls to avoid.")
]

# Cycle through topics across runs (not just weeks)
def get_next_topic():
    index = 0
    try:
        if os.path.exists(TOPIC_INDEX_FILE):
            with open(TOPIC_INDEX_FILE, "r") as f:
                index = int(f.read().strip())
        index = (index + 1) % len(TOPICS)
    except Exception:
        index = 0
    with open(TOPIC_INDEX_FILE, "w") as f:
        f.write(str(index))
    return TOPICS[index]

# Generate blog content with OpenAI
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

# Commit and push to GitHub
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
    category, prompt = get_next_topic()
    content = generate_post(prompt)
    save_post(category, content)
    push_to_github()

# Run immediately when script is called
if __name__ == "__main__":
    print("🚀 Running blog automation now...")
    run_blog_automation()

