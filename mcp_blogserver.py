import datetime
import os
import re
import frontmatter
from flask import Flask, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Blog prompt topics (rotates dynamically)
PROMPT_TOPICS = {
    "resume": "Write a blog post giving expert advice on how to write a modern, eye-catching resume that stands out in 2025. Include formatting tips, keywords, and examples. Make it engaging and helpful.",
    "college": "Write a well-formatted, engaging blog post for students applying to top-tier universities. Offer tips on how to write a standout college essay and include compelling section headings.",
    "grants": "Write a clean, informative blog post for small business owners on how to find and apply for grants in the US. Include top sources, application tips, and a professional tone."
}
topic_keys = list(PROMPT_TOPICS.keys())
topic_index = 0

app = Flask(__name__)

def make_slug(title):
    return re.sub(r"[^\w\s-]", "", title).strip().lower().replace(" ", "-")

def extract_title_and_body(content):
    lines = content.strip().split("\n")
    title = lines[0].strip("# ").strip()
    body = "\n".join(line.strip() for line in lines[1:] if line.strip())
    return title, body

def generate_unique_title(title):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{title} ({timestamp})"

def save_blog_post(title, body, topic):
    os.makedirs("_posts", exist_ok=True)
    title_with_timestamp = generate_unique_title(title)
    slug = make_slug(title)
    date_prefix = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-{slug}.md"
    filepath = os.path.join("_posts", filename)

    post = frontmatter.Post(body, **{
        "title": title_with_timestamp,
        "date": datetime.datetime.now().isoformat(),
        "tags": [topic, "ai-generated", "blog"],
        "topic": topic
    })

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))  # FIXED: using dumps to avoid write(bytes) error

    os.system("git add .")
    os.system(f"git commit -m 'Add new blog post: {title}'")
    os.system("git push")

    return filename

def generate_blog(topic=None):
    global topic_index

    if topic is None:
        topic = topic_keys[topic_index]
        topic_index = (topic_index + 1) % len(topic_keys)

    prompt = PROMPT_TOPICS[topic]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional blog writer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    full_content = response.choices[0].message.content.strip()
    title, body = extract_title_and_body(full_content)
    filename = save_blog_post(title, body, topic)

    return {"title": title, "file": filename}

@app.route("/generate", methods=["GET"])
def generate_rotating():
    return jsonify(generate_blog())

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
