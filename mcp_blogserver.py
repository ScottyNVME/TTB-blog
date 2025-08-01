import os
import json
import datetime
import re
import requests
import frontmatter
from flask import Flask, jsonify, request, render_template_string
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

app = Flask(__name__)

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")

PROMPT_TOPICS = {
    "resume": "Write a professional blog post about creating a modern, standout resume in today's job market. Use the following format: start with '## Crafting a Standout Resume', then include an introduction (~100 words), followed by three sections using '###' headers ('### Why Design Matters', '### What to Include', etc.), and finish with a '### Final Thoughts' conclusion. Use markdown formatting, callout examples, and short paragraphs to improve readability. Target 700 to 750 words.",
    "college": "Write a professional blog post about crafting a strong college application. Start with a title like '## How to Build a Winning College Application', then write an intro (~100 words), three well-organized sections using '###' headers, and a concluding '### Final Thoughts'. Format with markdown, include bullet points or examples if relevant, and ensure clear flow. Aim for 700 to 750 words.",
    "grants": "Write a professional blog post on winning grants. Begin with '## Guide to Winning Grants in 2025', write an engaging intro (~100 words), then break into 3 structured '###' sections with advice, and conclude with a '### Summary' or 'Final Thoughts' section. Use markdown, keep paragraphs tight and skimmable, and aim for 700 to 750 words total."
}
topic_keys = list(PROMPT_TOPICS.keys())
topic_index = 0

def load_style_sample():
    try:
        with open("style_sample.txt", "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""

def clean_title(text):
    return re.sub(r"[*_`~#]", "", text).strip()

def fetch_stock_image_url(topic):
    try:
        response = requests.get(
            f"https://api.unsplash.com/photos/random?query={topic}&orientation=landscape&client_id={UNSPLASH_ACCESS_KEY}"
        )
        if response.status_code == 200:
            data = response.json()
            return data["urls"]["regular"]
    except Exception as e:
        print(f"Error fetching stock image: {e}")
    return None

def fetch_ai_image_url(prompt):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        return response.data[0].url
    except Exception as e:
        print(f"Error generating AI image: {e}")
    return None

def insert_image_into_body(body, image_url, title):
    if not body.strip().lower().startswith("##"):
        body = f"## {title}\n\n" + body

    paragraphs = body.split("\n\n")
    if len(paragraphs) > 1:
        image_block = (
            f'<div style="float: right; width: 150px; margin-left: 1rem; margin-bottom: 1rem;">'
            f'<img src="{image_url}" alt="Related Image" '
            f'style="width: 100%; height: auto; border-radius: 8px;">'
            f'</div>'
        )
        paragraphs.insert(1, image_block)
    return "\n\n".join(paragraphs)

def generate_blog(topic=None, include_image=True):
    global topic_index
    if topic is None:
        topic = topic_keys[topic_index]
        topic_index = (topic_index + 1) % len(topic_keys)

    style_sample = load_style_sample()
    system_prompt = (
        "You are a helpful and professional blog writer. Use a well-structured markdown layout: a bold title ('## Title'), a 100-word intro, 2-3 clear '###' sections with strong subheadings, and a '### Final Thoughts' conclusion. Use short paragraphs, examples, and formatting that looks like a polished blog. Target 700 to 750 words."
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
    title = clean_title(title)

    if include_image:
        image_url = fetch_stock_image_url(topic)
        if not image_url:
            image_url = fetch_ai_image_url(f"Illustration for blog post about {topic}")
        if image_url:
            body = insert_image_into_body(body, image_url, title)

    filename = save_blog_post(title, body, topic)
    return {"title": title, "file": filename}

def extract_title_and_body(content):
    lines = content.strip().split("\n")
    if lines[0].lower().startswith("title:"):
        title = clean_title(lines[0][6:].strip())
        body = "\n".join(lines[1:]).strip()
    else:
        title = clean_title(lines[0].strip())
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
    return render_template_string("""
        <h1>📝 MCP Blog Generator</h1>
        <form action="/generate-ui" method="get">
            <label for="topic">Select Topic:</label>
            <select name="topic" id="topic">
                {% for key in topics %}
                    <option value="{{ key }}">{{ key.capitalize() }}</option>
                {% endfor %}
            </select><br><br>
            <label><input type="checkbox" name="image" checked> Include Image</label><br><br>
            <button type="submit">Generate Blog</button>
        </form>
    """, topics=topic_keys)

@app.route("/generate-ui", methods=["GET"])
def generate_ui():
    topic = request.args.get("topic", "resume").lower()
    include_image = request.args.get("image") == "on"
    result = generate_blog(topic, include_image=include_image)
    return f"<h2>✅ Blog Generated</h2><p><b>Title:</b> {result['title']}</p><p><b>File:</b> {result['file']}</p><p><a href='/'>⬅️ Back</a></p>"

@app.route("/generate", methods=["GET"])
def generate_next():
    include_image = request.args.get("image", "true").lower() != "false"
    return jsonify(generate_blog(include_image=include_image))

@app.route("/generate/<topic>", methods=["GET"])
def generate_by_topic(topic):
    topic = topic.lower()
    if topic not in PROMPT_TOPICS:
        return jsonify({"error": "Unsupported topic."}), 400
    include_image = request.args.get("image", "true").lower() != "false"
    global topic_index
    topic_index = topic_keys.index(topic)
    return jsonify(generate_blog(topic, include_image=include_image))

if __name__ == "__main__":
    app.run(debug=True)
