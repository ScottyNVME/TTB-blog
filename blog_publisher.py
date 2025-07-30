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

# Random tone variations for title creativity
tone_styles = ["playful", "thoughtful", "provocative", "professional"]

def generate_title(topic):
    tone = random.choice(tone_styles)
    title_prompt = (
        f"Write a {tone} blog post title for the topic '{topic}'. "
        f"Avoid clichés like 'in 2025', 'guide to', 'navigating'. Make it original, catchy, and natural."
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

    print(f"🧠 Generating blog post for topic: {topic}")
    date_str = datetime.date.today().strftime("%Y-%m-%d")

    # Generate content
    content_prompt = f"Write a blog post about: {title}. Make it informative, engaging, and around 500-800 words."
    content_response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content_prompt}]
    )
    markdown_content = md.markdownify(content_response.choices[0].message.content.strip())

    # Generate image
    dalle_prompt = f"Create an illustrative blog image concept for the article titled '{title}'."
    dalle_response = openai.images.generate(
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    image_url = dalle_response.data[0].url
    image_filename = f"{date_str}-{topic.replace(' ', '-')}.png"
    image_path = f"assets/images/{image_filename}"

    image_data = requests.get(image_url).content
    with open(image_path, "wb") as f:
        f.write(image_data)

    # Save blog markdown
    markdown_file = f"_posts/{date_str}-title-{title.replace(' ', '-').lower()}.md"
    with open(markdown_file, "w") as f:
        f.write(f"""---
layout: post
title: \"{title.replace('"', "'")}\"
date: {date_str}
image: /assets/images/{image_filename}
---

""")
        f.write(markdown_content)

    print(f"✅ Blog post saved: {markdown_file}")
    return markdown_file

def main():
    print("🚀 Running blog automation now...")
    result = generate_blog_post()
    if result:
        print("🛄🏼 Committing and pushing to GitHub...")
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "Automated blog post"])

        # Pull latest changes before pushing
        subprocess.run(["git", "pull", "--rebase", "origin", "main"])

        # Push to GitHub
        subprocess.run(["git", "push", "origin", "main"])
        print("✅ Changes pushed to GitHub!")
        print("🎉 Blog generation complete.")

if __name__ == "__main__":
    main()
