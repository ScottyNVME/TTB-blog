import os
import openai
import datetime
import requests
import re
from dotenv import load_dotenv
import subprocess
import random

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Blog topics to choose from
TOPICS = [
    "resume tips",
    "college essay advice",
    "scholarship and grant opportunities",
    "fellowships",
    "LinkedIn optimization",
    "interview tips",
    "career pivots",
    "remote work",
    "side hustles",
    "personal branding"
]

# Random tone styles for title generation
tone_styles = ["playful", "thoughtful", "provocative", "professional"]

# Helper to slugify title for filenames
def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

# Remove bold markdown artifacts like **this**
def clean_markdown(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\1', text)

# Generate a creative blog title
def generate_title(topic):
    tone = random.choice(tone_styles)
    title_prompt = (
        f"Write a {tone} blog post title for the topic '{topic}'. "
        f"Avoid clichés like 'in 2025', 'guide to', or 'navigating'. Make it catchy and natural."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": title_prompt}]
    )
    return response.choices[0].message.content.strip()

# Generate the full blog post
def generate_blog_post():
    topic = random.choice(TOPICS)
    title = generate_title(topic)

    while True:
        print(f"\n📝 Preview Title: {title}")
        confirm = input("Do you want to continue with this title? (y = yes / r = refresh / n = cancel): ").strip().lower()
        if confirm == "y":
            break
        elif confirm == "r":
            topic = random.choice(TOPICS)
            title = generate_title(topic)
        else:
            print("❌ Blog generation cancelled.")
            return None

    print("\n🚀 Generating blog content...")
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    content_prompt = (
        f"Write a blog post titled: {title}. "
        f"Make it engaging, informative, and flow well with clean Markdown formatting. "
        f"Use proper headers (##), bullets, spacing. No bold formatting (**text**) please."
    )
    content_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content_prompt}]
    )
    markdown_content = clean_markdown(content_response.choices[0].message.content.strip())

    # Generate and save image
    dalle_prompt = f"Create an illustrative blog image concept for the article titled '{title}'."
    dalle_response = openai.images.generate(prompt=dalle_prompt, n=1, size="1024x1024")
    image_url = dalle_response.data[0].url
    image_filename = f"{date_str}-{slugify(topic)}.png"
    image_path = f"assets/images/{image_filename}"
    image_data = requests.get(image_url).content
    with open(image_path, "wb") as f:
        f.write(image_data)

    # Save blog post file
    slug = slugify(title)
    markdown_file = f"_posts/{date_str}-title-{slug}.md"
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(f"""---
layout: post
title: "{title}"
date: {date_str}
image: /assets/images/{image_filename}
---

# {title}

{markdown_content}
""")

    print(f"✅ Blog post saved to: {markdown_file}")
    return markdown_file

# Push to GitHub
def main():
    result = generate_blog_post()
    if result:
        print("📦 Committing and pushing to GitHub...")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Automated blog post"])
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])
        subprocess.run(["git", "push", "origin", "main"])
        print("✅ Blog pushed to GitHub successfully!")

if __name__ == "__main__":
    main()
