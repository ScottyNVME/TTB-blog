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

# Rotate topic based on an index file for better tracking
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

# Create topic-specific prompt using your writing style and date
def generate_prompt(topic):
    today = datetime.date.today()
    current_month = today.strftime("%B")
    current_year = today.year

    # Load your writing style sample
    with open("style_sample.txt", "r") as f:
        style = f.read().strip()

    if topic == "resume":
        return (
            f"Write a fresh 700–750 word blog post on resume writing using the writing style shown below. "
            f"Reflect new hiring trends, job market shifts, formatting best practices, action verbs, and tone for {current_month} {current_year}. "
            f"Ensure the post is timely, practical, original, and ends with a soft call to action pointing to tothroughbeyond.com.\n\n"
            f"Writing Style Example:\n{style}"
        )
    elif topic == "essays":
        return (
            f"Write a compelling 700–750 word blog post about crafting strong college essays. Match the tone and sentence flow of the writing sample provided below. "
            f"Offer fresh advice on authenticity, structure, storytelling, and writing tips relevant to students in {current_month} {current_year}. "
            f"Finish with a call to action leading readers to tothroughbeyond.com.\n\n"
            f"Writing Style Example:\n{style}"
        )
    elif topic == "grants":
        return (
            f"Write a 700–750 word blog post about finding and applying for college grants or scholarships. Use the writing style from the sample below. "
            f"Incorporate relevant resources, deadlines, or new funding trends relevant to {current_month} {current_year}. "
            f"Make it informative but relatable. Close with a soft CTA pointing to tothroughbeyond.com.\n\n"
            f"Writing Style Example:\n{style}"
        )

# Generate blog content from OpenAI
def generate_post(prompt):
    print(f"🧠 Generating blog post...")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Save post to markdown with front matter
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

# Git automation with safe pull/push
def push_to_github():
    print("📤 Committing and pushing to GitHub...")
    repo_path = "/Users/savedis/Documents/TTB-blog"
    subprocess.run(["git", "add", "."], cwd=repo_path)
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd=repo_path)
    subprocess.run(["git", "pull", "--rebase"], cwd=repo_path)
    subprocess.run(["git", "push", "--set-upstream", "origin", "main"], cwd=repo_path)
    print("✅ Changes pushed to GitHub!")

# Main runner
def run_blog_automation():
    print("🚀 Running blog automation now...")
    category = get_topic_from_index()
    prompt = generate_prompt(category)
    content = generate_post(prompt)
    save_post(category, content)
    push_to_github()

if __name__ == "__main__":
    run_blog_automation()
