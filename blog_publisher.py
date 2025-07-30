import os
import openai
import requests
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import random
import re
import subprocess

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Define topics
topics = [
    "resume writing",
    "college admissions essays",
    "grants and scholarships",
    "career growth strategies",
    "interview tips",
    "professional networking",
    "LinkedIn optimization",
    "fellowship applications"
]

# Dynamically select a topic
topic = random.choice(topics)

# Get current date
today = datetime.today().strftime('%Y-%m-%d')
month_year = datetime.today().strftime('%B %Y')

# Generate prompt
prompt = (
    f"Write a fresh 700–750 word blog post about {topic}. "
    f"Make sure it's relevant to {month_year}, based on real-world events, news, or job trends. "
    f"Reference current best practices, industry terms, or formats relevant to this topic. "
    f"Make it engaging, inspiring, and practical. Include a short call to action to visit tothroughbeyond.com. "
    f"Base the writing style on previous TTB blog posts. Write in Markdown format."
)

# Print running status
print("🚀 Running blog automation now...")
print(f"🧠 Generating blog post for topic: {topic}")

# OpenAI client setup
client = openai.OpenAI()

def generate_blog_post(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Generate blog content
content = generate_blog_post(prompt)

# Extract title from first line
def extract_title(markdown_text):
    match = re.match(r"#\s+(.*)", markdown_text)
    return match.group(1).strip() if match else "Untitled"

title = extract_title(content)
slug = re.sub(r"[^\w]+", "-", title.lower()).strip("-")
filename = f"{today}-title-{slug}.md"

# Generate DALLE image
def generate_image(prompt_text, filename_slug):
    dalle_prompt = f"Professional, clean, blog cover image for: {prompt_text}"
    response = client.images.generate(
        model="dall-e-3",
        prompt=dalle_prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    image_filename = f"{filename_slug}.png"
    image_path = f"assets/images/{image_filename}"
    with open(image_path, "wb") as f:
        f.write(requests.get(image_url).content)
    return f"https://scottynvme.github.io/TTB-blog/{image_path}"

# Generate and download image
image_url = generate_image(title, slug)

# Add frontmatter to content
frontmatter = f"""---
title: "{title}"
date: {today}
categories: {topic}
image: "{image_url}"
---

"""

# Save blog post
output_path = f"_posts/{filename}"
with open(output_path, "w") as f:
    f.write(frontmatter + content)

print(f"✅ Blog post saved: {output_path}")

# Update topic index (optional text index)
with open("topic_index.txt", "a") as index_file:
    index_file.write(f"{today} - {title} - {topic}\n")

# Git commit and push
print("🌐 Committing and pushing to GitHub...")

try:
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Automated blog post"], check=True)
    subprocess.run(["git", "pull", "--rebase"], check=True)
    subprocess.run(["git", "push"], check=True)
    print("✅ Changes pushed to GitHub!")
except subprocess.CalledProcessError as e:
    print("❌ Git push failed. Please check for conflicts or remote changes.")
    print(e)

