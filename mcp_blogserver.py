import os
import json
import datetime
import frontmatter
from flask import Flask, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

app = Flask(__name__)

PROMPT_TOPICS = {
    "resume": "Write a professional blog post about creating a modern, standout resume in today's job market.",
    "college": "Write an insightful and inspiring blog post about preparing a strong college application.",
    "grants": "Write a helpful blog post on how to apply for and win educational or small business grants.",
}
topic_keys = list(PROMPT_TOPICS.keys())
topic_index = 0

def load_style_sample():
    try:
        with open("style_sample.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def generate_blog(topic=None):
    global topic_index
    if topic is None:
        topic = topic_keys[topic_index]
        topic_index = (topic_index + 1) % len(topic_keys)

    style_sample = load_style_sample()
    system_prompt = (
        "You are a helpful and professional blog writer. Format your writing with clean paragraphs, bold headings, and clear structure."
    )
    if style_sample:
        system_prompt += f"\nMatch the tone and flow of the following writing sample:\n---\n{style_sample}\n---"

    user_prompt = PROMPT_TOPICS[topic]
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.9
    )

    full_content = response.choices[0].message.content.strip()
    title, body = extract_title_and_body(full_content)
    filename = save_blog_post(title, body, topic)
    return {"title": title, "file": filename}

def extract_title_and_body(content):
    lines = content.strip().split("\n")
    if lines[0].lower().startswith("title:"):
        title = lines[0][6:].strip()
        body = "\n".join(lines[1:]).strip()
    else:
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
    return title, body

def slugify(text):
    return (
        text.lower()
        .replace(" ", "-")
        .replace(":", "")
        .replace("'", "")
        .replace(",", "")
        .replace(".", "")
        .replace("*", "")
    )

def save_blog_post(title, body, topic):
    slug = slugify(title)
    date = datetime.datetime.now().date()
    filename = f"{date}-{slug}.md"
    filepath = os.path.join("_posts", filename)

    try:
        post = frontmatter.Post(body, **{
            "title": title,
            "tags": [topic, "ai-generated", "blog"],
            "date": datetime.datetime.now().isoformat(),
            "topic": topic
        })

        os.makedirs("_posts", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter.dumps(post))

        os.system("git add .")
        os.system(f"git commit -m 'Add new blog post: {title}'")
        os.system("git push")

    except Exception as e:
        print(f"Error saving blog post: {e}")

    return filename

@app.route("/", methods=["GET"])
def homepage():
    return "<h1>📝 MCP Blog Generator is running!</h1><p>Try <code>/generate</code> or <code>/generate/resume</code></p>"

@app.route("/generate", methods=["GET"])
def generate_next():
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
