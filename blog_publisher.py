import os
import openai
import datetime
import requests
import markdownify
from dotenv import load_dotenv
import random
import subprocess
import re

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

# Random tone variations
tone_styles = ["playful", "thoughtful", "provocative", "professional"]

def generate_title(topic):
    tone = random.choice(tone_styles)
    prompt = (
        f"Write a {tone} blog post title for the topic '{topic}'. "
        f"Avoid clichés like 'in 2025', 'guide to', or 'navigating'. Make it original, catchy, and natural."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().strip('"')

def clean_markdown(md_content):
    # Remove bold markdown (**text**) to avoid messy formatting
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", md_content)
    return cleaned

def slugify(title):
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug

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
            print("❌ Blog generation cancelled by user.")
            return None

    print("\n🚀 Running blog automation now...")
    print(f"🧠 Generating blog post for topic: {topic}")
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Generate content
    content_prompt = f"Write an engaging blog post titled: {title}. Keep it informative, polished, and 500-800 words. Use numbered or bulleted lists when helpful."
    content_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content_prompt}]
    )
    raw_content = content_response.choices[0].message.content.strip()
    markdown_content = markdownify.markdownify(raw_content)
    markdown_content = clean_markdown(markdown_content)

    # Generate image
    dalle_prompt = f"Create an illustrative blog image concept for the article titled '{title}'."
    dalle_response = openai.images.generate(
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = dalle_response.data[0].url
    image_slug = slugify(topic)
    image_filename = f"{date_str}-{image_slug}.png"
    image_path = f"assets/images/{image_filename}"

    image_data = requests.get(image_url).content
    with open(image_path, "wb") as f:
        f.write(image_data)

    # Save blog markdown
    file_slug = slugify(title)
    markdown_file = f"_posts/{date_str}-{file_slug}.md"
    with open(markdown_file, "w", encoding="utf-8") as f:
        f.write(f"""---
layout: post
title: '{title}'
date: {date_str}
image: /assets/images/{image_filename}
---

{markdown_content}
""")

    print(f"✅ Blog post saved: {markdown_file}")
    return markdown_file

def main():
    result = generate_blog_post()
    if result:
        print("💽 Committing and pushing to GitHub...")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Automated blog post"])
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])
        subprocess.run(["git", "push", "origin", "main"])
        print("✅ Changes pushed to GitHub!")
        print("🎉 Blog generation complete.")

if __name__ == "__main__":
    main()
