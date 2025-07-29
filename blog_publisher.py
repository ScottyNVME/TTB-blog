import os
import openai
import datetime
import subprocess
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants
BLOG_DIR = "/Users/savedis/Documents/TTB-blog/_posts"
IMAGE_DIR = "/Users/savedis/Documents/TTB-blog/assets/images"
TOPICS = ["grants", "resume", "essays"]

# Rotate through topics using an index
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

# Inject your writing style into the prompt
def generate_prompt(topic):
    today = datetime.date.today()
    current_month = today.strftime("%B")
    current_year = today.year

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

# Generate image using DALL·E
def generate_image(prompt, filename):
    print("🖼️ Generating image...")
    response = openai.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    image_path = os.path.join(IMAGE_DIR, filename)

    img_data = requests.get(image_url).content
    with open(image_path, 'wb') as handler:
        handler.write(img_data)

    print(f"✅ Image saved: {image_path}")
    return f"/assets/images/{filename}"

# Use GPT to write the blog content
def generate_post(prompt):
    print("🧠 Generating blog post...")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Save blog and image to markdown
def save_post(category, content):
    today = datetime.date.today()
    title = content.splitlines()[0].strip().replace("**", "")
    slug = title.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("–", "-")
    filename = f"{today.strftime('%Y-%m-%d')}-{slug[:50]}.md"
    filepath = os.path.join(BLOG_DIR, filename)
    image_filename = f"{slug[:50]}.png"
    image_path = generate_image(f"Illustration for a blog post about {category}", image_filename)

    with open(filepath, "w") as f:
        f.write(f"---\n")
        f.write(f"title: \"{title}\"\n")
        f.write(f"layout: post\n")
        f.write(f"categories: {category}\n")
        f.write(f"image: {image_path}\n")
        f.write(f"---\n\n")
        f.write(f"![{title}]({image_path})\n\n")
        f.write(content)

    print(f"✅ Blog post saved: {filepath}")
    return filepath

# Commit and push to GitHub
def push_to_github():
    print("📤 Committing and pushing to GitHub...")
    repo_path = "/Users/savedis/Documents/TTB-blog"
    subprocess.run(["git", "add", "."], cwd=repo_path)
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd=repo_path)
    subprocess.run(["git", "pull", "--rebase"], cwd=repo_path)
    subprocess.run(["git", "push", "--set-upstream", "origin", "main"], cwd=repo_path)
    print("✅ Changes pushed to GitHub!")

# Main flow
def run_blog_automation():
    print("🚀 Running blog automation now...")
    category = get_topic_from_index()
    prompt = generate_prompt(category)
    content = generate_post(prompt)
    save_post(category, content)
    push_to_github()

if __name__ == "__main__":
    run_blog_automation()
