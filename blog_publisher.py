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
TOPIC_INDEX_FILE = "topic_index.txt"
TOPICS = [
    ("grants", "Write a fresh 700–750 word blog post about college grants, scholarships, or funding opportunities. Include relevant updates, policy changes, or new programs as of {month_year}. Highlight practical tips, eligibility criteria, and current keyword trends in financial aid. Include a short CTA to learn more at tothroughbeyond.com."),
    ("resume", "Write a fresh 700–750 word blog post on resume writing that reflects new hiring trends or job market shifts. Reference current formatting expectations, action verbs, or examples used in recent top-tier resumes. Make it engaging, original, and practical for job seekers. Ensure that the advice is timely and relevant for {month_year}, and incorporates or is inspired by currently trending keywords in the topic. Add a short call to action encouraging readers to learn more at tothroughbeyond.com."),
    ("essays", "Write a fresh 700–750 word blog post on writing a compelling college admissions essay. Include advice based on {month_year} trends, what top schools are valuing, and how to stand out with voice, story, and structure. Include examples and inspiration drawn from trending application topics. End with a CTA to visit tothroughbeyond.com for help.")
]

# Get current month and year
month_year = datetime.date.today().strftime("%B %Y")

# Track and rotate topic based on last index
def get_next_topic():
    index = 0
    if os.path.exists(TOPIC_INDEX_FILE):
        with open(TOPIC_INDEX_FILE, "r") as f:
            index = int(f.read().strip())
    next_index = (index + 1) % len(TOPICS)
    with open(TOPIC_INDEX_FILE, "w") as f:
        f.write(str(next_index))
    category, prompt_template = TOPICS[index]
    return category, prompt_template.format(month_year=month_year)

# Generate DALLE image URL
def generate_image(prompt, image_filename):
    print("🎨 Generating cover image...")
    response = openai.images.generate(
        model="dall-e-3",
        prompt=f"Illustration or photo for blog topic: {prompt}",
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url

    # Download and save image locally
    image_path = f"/Users/savedis/Documents/TTB-blog/assets/images/{image_filename}"
    img_data = requests.get(image_url).content
    with open(image_path, 'wb') as handler:
        handler.write(img_data)

    print(f"🖼️ Image saved: {image_path}")
    return f"https://scottynvme.github.io/TTB-blog/assets/images/{image_filename}"

# Generate blog content
def generate_post(prompt):
    print(f"🧠 Generating blog post for prompt: {prompt}")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

# Save post to file
def save_post(category, content, image_url):
    today = datetime.date.today()
    title = content.splitlines()[0].strip().replace("*", "")
    slug = title.lower().replace(" ", "-").replace(":", "").replace("?", "").replace("–", "-")
    filename = f"{today.strftime('%Y-%m-%d')}-{slug[:40]}.md"
    filepath = os.path.join(BLOG_DIR, filename)

    with open(filepath, "w") as f:
        f.write("---\n")
        f.write(f"title: \"{title}\"\n")
        f.write("layout: post\n")
        f.write(f"categories: {category}\n")
        f.write("---\n\n")
        f.write(f"![{title}]({image_url})\n\n")
        f.write(content)

    print(f"✅ Blog post saved: {filepath}")
    return filepath

# Git push with sync
def push_to_github():
    print("📤 Committing and pushing to GitHub...")
    subprocess.run(["git", "add", "."], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "commit", "-m", "Automated blog post"], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "pull", "--rebase"], cwd="/Users/savedis/Documents/TTB-blog")
    subprocess.run(["git", "push"], cwd="/Users/savedis/Documents/TTB-blog")
    print("✅ Changes pushed to GitHub!")

# Main
def run_blog_automation():
    category, prompt = get_next_topic()
    content = generate_post(prompt)
    image_filename = f"{datetime.date.today().strftime('%Y-%m-%d')}-{category}.png"
    image_url = generate_image(prompt, image_filename)
    save_post(category, content, image_url)
    push_to_github()

if __name__ == "__main__":
    print("🚀 Running blog automation now...")
    run_blog_automation()
