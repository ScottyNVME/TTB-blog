import os
import openai
import datetime
import requests
import re
from dotenv import load_dotenv
import random
import subprocess

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

tone_styles = ["playful", "thoughtful", "provocative", "professional"]

def generate_title(topic):
    tone = random.choice(tone_styles)
    prompt = f"Write a {tone} blog post title for the topic '{topic}'. Avoid clichés and keep it engaging but natural."
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def clean_content(text):
    # Remove markdown bold markers
    text = text.replace("**", "")
    
    # Convert numbered headers to h3
    text = re.sub(r'^(\d+)\.\s*(.*?)$', r'### \1. \2', text, flags=re.MULTILINE)

    # Convert bullet points with bold headers to dash format
    text = re.sub(r'^- \*\*(.+?)\*\*:', r'- \1:', text, flags=re.MULTILINE)
    
    return text.strip()

def sanitize_filename(title):
    return re.sub(r"[^a-zA-Z0-9\-]", "", title.replace(" ", "-")).lower()

def generate_blog_post():
    topic = random.choice(TOPICS)
    title = generate_title(topic)

    while True:
        print(f"\n📝 Preview Title: {title}")
        confirm = input("Use this title? (y = yes / r = refresh / n = cancel): ").strip().lower()
        if confirm == "y":
            break
        elif confirm == "r":
            topic = random.choice(TOPICS)
            title = generate_title(topic)
        else:
            print("❌ Blog generation cancelled.")
            return None

    print(f"\n🚀 Generating blog post for topic: {topic}")
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    prompt = f"Write a 500-800 word blog post titled '{title}' without including the title at the top. Make it professional, informative, and engaging with section headers and bullet lists where helpful."
    content_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    raw_content = content_response.choices[0].message.content.strip()
    clean_blog = clean_content(raw_content)

    # Generate image using DALL·E
    dalle_prompt = f"Create a blog image for an article titled '{title}'."
    dalle_response = openai.images.generate(
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = dalle_response.data[0].url
    image_filename = f"{date_str}-{topic.replace(' ', '-')}.png"
    image_path = f"assets/images/{image_filename}"

    try:
        image_data = requests.get(image_url).content
        with open(image_path, "wb") as f:
            f.write(image_data)
    except Exception as e:
        print(f"⚠️ Image download failed: {e}")
        image_path = ""

    # Save markdown
    safe_title = title.replace('"', "'")
    slug_title = sanitize_filename(title)
    markdown_path = f"_posts/{date_str}-{slug_title}.md"
    with open(markdown_path, "w", encoding="utf-8") as f:
        f.write(f"""---
layout: post
title: "{safe_title}"
date: {date_str}
image: /{image_path}
---

### {title}

{clean_blog}
""")

    print(f"✅ Blog post saved to: {markdown_path}")
    return markdown_path

def main():
    result = generate_blog_post()
    if result:
        print("💽 Committing and pushing to GitHub...")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Automated blog post"])
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])
        subprocess.run(["git", "push", "origin", "main"])
        print("✅ Published!")

if __name__ == "__main__":
    main()
