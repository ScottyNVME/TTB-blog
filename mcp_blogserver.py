import os
import re
import datetime
import random
import frontmatter
from flask import Flask, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# 🌱 Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📚 Blog topics
PROMPT_TOPICS = {
    "resume": "Write a polished, well-formatted blog post about resume tips for job seekers today. Use proper spacing, markdown structure, and remove all asterisks. Title the post clearly.",
    "college": "Write a blog post about how students can write better college application essays. Make it sound professional, engaging, and cleanly formatted in markdown.",
    "grants": "Write a blog post about the most common mistakes people make when applying for grants. Make it easy to follow and format it cleanly as a blog article."
}
topic_keys = list(PROMPT_TOPICS.keys())
topic_index = 0  # 🔁 Rotation index

# 🚀 Flask app
app = Flask(__name__)

def generate_blog(topic):
    prompt = PROMPT_TOPICS[topic]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional blog writer who formats posts cleanly."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    full_content = response.choices[0].message.content.strip()
    title, body = extract_title_and_body(full_content)
    filename = save_blog_post(title, body, topic)
    return {"title": title, "file": filename}

def extract_title_and_body(content):
    lines = content.split("\n")
    title_line = lines[0].strip()
    if title_line.startswith("# "):
        title = title_line[2:].strip()
        body = "\n".join(lines[1:]).strip()
    else:
        title = title_line
        body = "\n".join(lines[1:]).strip()

    body = re.sub(r"\*\*(.*?)\*\*", r"\1", body)  # 🧹 Remove bold markers
    return title, body

def make_slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def is_title_duplicate(new_title):
    existing_files = os.listdir("posts")
    new_slug = make_slug(new_title)
    for fname in existing_files:
        if new_slug in fname:
            return True
    return False

def generate_unique_title(title):
    base = title
    suffix = 1
    while is_title_duplicate(title):
        title = f"{base} ({suffix})"
        suffix += 1
    return title

def save_blog_post(title, body, topic):
    os.makedirs("posts", exist_ok=True)
    title = generate_unique_title(title)
    slug = make_slug(title)
    date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-{slug}.md"
    filepath = os.path.join("posts", filename)

    post = frontmatter.Post(body, **{
        "title": title,
        "date": datetime.datetime.now().isoformat(),
        "topic": topic
    })

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    # 🔁 Auto git push
    os.system("git add .")
    os.system(f"git commit -m 'Add new blog post: {title}'")
    os.system("git push")

    return filename

@app.route("/generate", methods=["GET"])
def generate_rotating():
    global topic_index
    topic = topic_keys[topic_index]
    topic_index = (topic_index + 1) % len(topic_keys)
    return jsonify(generate_blog(topic))

@app.route("/generate/<topic>", methods=["GET"])
def generate_by_topic(topic):
    topic = topic.lower()
    if topic not in PROMPT_TOPICS:
        return jsonify({"error": "Unsupported topic."}), 400
    global topic_index
    topic_index = topic_keys.index(topic)
    return jsonify(generate_blog(topic))

if __name__ == "__main__":
    app.run(debug=True)
