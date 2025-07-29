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
    "grants",
    "resume",
    "essays"
]

# Rotate topic based on ISO week number
def get_weekly_topic():
    week_number = datetime.date.today().isocalendar()[1]
    return TOPICS[week_number % len(TOPICS)]

# Load or create topic index to cycle evenly through topics
def get_topic_from_index():
    index_file = "topic_index.txt"
    if os.path.exists(index_file):
        with open(index_file, "r") as f:
            index = int(f.read().strip())
    else:
        index = 0

    topic = TOPICS[index % len(TOPICS)]

    with open(index_file, "w") as f:
        f.write(str((index + 1) % len(TOPICS)))

    return topic

# Create topic-specific prompt with current date
def generate_prompt(topic):
    today = datetime.date.today()
    current_month = today.strftime("%B")
    current_year = today.year

    if topic == "resume":
        return (
            f"Write a fresh 700–750 word blog post on resume writing that reflects new hiring trends "
            f"or job market shifts. Reference current formatting expectations, action verbs, or examples used "
            f"in recent top-tier resumes. Make it engaging, original, and practical for job seekers. "
            f"Ensure that the advice is timely and relevant for {current_month} {current_year}, and incorporates "
            f"or is inspired by currently trending keywords in the topic. Add a short call to action encouraging readers "
            f"to learn more at tothroughbeyond.com."
        )
    elif topic == "essays":
        return (
            f"Write a compelling 700–750 word blog post about how to write a standout college admissions essay. "
            f"Focus on techniques that are timely for {current_month} {current_year} applicants, including recent prompts, "
            f"examples from successful essays, or advice tailored to trends in selective school admissions. Include trending keywords "
            f"or angles that may be popular in the news or education space, and end with a short call to action to visit tothroughbeyond.com."
        )
    elif topic == "grants":
        return (
            f"Write a 700–750 word blog post about college grants, scholarships, or student funding options that are relevant in {current_month} {current_year}. "
            f"Highlight any recent updates in federal or private programs, trending searches, or seasonal application advice. "
            f"Use trending financial aid keywords and give readers a reason to check out tothroughbeyond.com."
        )

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
    title = content.splitlines()[0].strip().replace("**", "")
    slug = title.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("–", "-")
    filename = f"{today.strftime('%Y-%m-%d')}-{slug[:50]}.md"
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

# Commit and push to GitHub (rebase-safe)
def push_to_github():
    print("📤 Committing and pushing to GitHub...")
    repo_path = "/Users/savedis/Documents/TTB-blog"

    subprocess.run(["git", "add", "."], cwd=repo_path)
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd=repo_path)

    # Safe pull to rebase with remote before pushing
    subprocess.run(["git", "pull", "--rebase"], cwd=repo_path)

    # Now push your changes
    subprocess.run(["git", "push", "--set-upstream", "origin", "main"], cwd=repo_path)
    print("✅ Changes pushed to GitHub!")

# Main automation function
def run_blog_automation():
    print("🚀 Running blog automation now...")
    category = get_topic_from_index()
    prompt = generate_prompt(category)
    content = generate_post(prompt)
    save_post(category, content)
    push_to_github()

# Run when script is executed
if __name__ == "__main__":
    run_blog_automation()
