import os
import openai
import datetime
import requests
import markdownify as md
from dotenv import load_dotenv
import random
import subprocess

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

# Tone styles for title variety
tone_styles = ["playful", "thoughtful", "provocative", "professional"]

def generate_title(topic):
    tone = random.choice(tone_styles)
    title_prompt = (
        f"Write a {tone} blog post title for the topic '{topic}'. "
        f"Make it original and catchy. Avoid overused phrases like '2025 guide', 'navigating', or 'ultimate'."
    )
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": title_prompt}]
    )
    return response.choices[0].message.content.strip()

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

    print(f"\n🚀 Running blog automation...")
    print(f"🧠 Generating blog post for topic: {topic}")
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Generate blog content
    content_prompt = (
        f"Write an engaging, informative blog post titled '{title}'. "
        f"Use clear formatting with numbered or bulleted lists, strong section headings, and natural tone. "
        f"Make it 600–800 words long and current as of {datetime.datetime.now().strftime('%B %Y')}."
    )
    content_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content_prompt}]
    )
    raw_text = content_response.choices[0].message.content.strip()

    # Convert to markdown with improved formatting
    markdown_content = md.markdownify(
        raw_text,
        bullets='*',
        strong_em_symbol='**',
        heading_style="ATX"
    )

    # Generate image via DALL·E
    dalle_prompt = f"Create an illustrative blog image for the article titled '{title}'."
    dalle_response = openai.images.generate(
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = dalle_response.data[0].url
    image_filename = f"{date_str}-{topic.replace(' ', '-')}.png"
    image_path = f"assets/images/{image_filename}"
    image_web_path = f"/assets/images/{image_filename}"

    # Download image
    image_data = requests.get(image_url).content
    os.makedirs("assets/images", exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(image_data)

    # Save blog markdown
    slug_title = title.replace(" ", "-").replace(":", "").replace("?", "").replace("/", "").lower()
    markdown_file_path = f"_posts/{date_str}-{slug_title[:40]}.md"
    with open(markdown_file_path, "w", encoding="utf-8") as f:
        f.write(f"""---
layout: post
title: "{title.replace('"', "'")}"
date: {date_str}
image: {image_web_path}
---

# {title}

{markdown_content}
""")

    print(f"✅ Blog post saved: {markdown_file_path}")
    return markdown_file_path

def main():
    post_path = generate_blog_post()
    if post_path:
        print("💽 Committing and pushing to GitHub...")

        # Git operations
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Automated blog post"], check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("✅ Blog post pushed to GitHub!")
        print("🎉 Done.")

if __name__ == "__main__":
    main()
