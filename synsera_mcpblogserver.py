import os
import json
import datetime
import re
import requests
import frontmatter
import tempfile
import threading
from flask import Flask, jsonify, request, render_template_string, Response, redirect
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

app = Flask(__name__)

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

progress = {"value": 0}

@app.route("/", methods=["GET"])
def generate_ui():
    return render_template_string("""
        <html>
        <head>
            <title>Synsera Blog Generator</title>
            <style>
                body { font-family: sans-serif; padding: 40px; background: #f9f9f9; color: #333; }
                h1 { font-size: 2.2em; }
                label, select, input, button, textarea { font-size: 1em; margin: 10px 0; display: block; width: 100%; max-width: 600px; }
                .progress-bar-wrapper { width: 100%; background: #ddd; border-radius: 4px; overflow: hidden; height: 20px; margin-top: 10px; }
                .progress-bar-fill { height: 100%; width: 0%; transition: width 0.3s ease-in-out; background: red; }
            </style>
            <script>
                async function pollProgress() {
                    const res = await fetch("/progress");
                    const data = await res.json();
                    const bar = document.getElementById("progress-bar");
                    bar.style.width = data.value + "%";
                    bar.style.backgroundColor = `rgb(${255 - 2.5 * data.value}, ${2.5 * data.value}, 0)`;
                }
                function onSubmitForm() {
                    setInterval(pollProgress, 500);
                }
            </script>
        </head>
        <body>
            <h1>📝 Synsera MCP Blog Generator</h1>
            <form action="/generate" method="post" enctype="multipart/form-data" onsubmit="onSubmitForm()">
                <label for="custom_prompt">Describe Your Blog Topic or Goal:</label>
                <textarea name="custom_prompt" id="custom_prompt" rows="4" placeholder="e.g. I want a friendly blog post about tips for small businesses using AI tools."></textarea>

                <label for="tone">Tone (e.g. friendly, professional, fun, inspiring):</label>
                <input type="text" name="tone" id="tone" placeholder="fun, witty, informative...">

                <label for="audience">Target Audience:</label>
                <input type="text" name="audience" id="audience" placeholder="e.g. startup founders, job seekers, students">

                <label for="length">Desired Length (in words):</label>
                <input type="number" name="length" id="length" placeholder="e.g. 750">

                <label><input type="checkbox" name="include_image" checked> Include Image</label>

                <label for="image_style">Image Style (e.g. stock, DALL·E, banner, none):</label>
                <input type="text" name="image_style" id="image_style" placeholder="banner">

                <label>Upload Reference File (optional):</label>
                <input type="file" name="file">

                <label for="reference_url">Reference Website URL (optional):</label>
                <input type="url" name="reference_url" id="reference_url" placeholder="https://example.com">

                <div class="progress-bar-wrapper">
                    <div id="progress-bar" class="progress-bar-fill"></div>
                </div>

                <button type="submit">Generate Blog</button>
            </form>
        </body>
        </html>
    """)

@app.route("/progress")
def get_progress():
    return jsonify(progress)

@app.route("/generate", methods=["POST"])
def generate_blog():
    progress["value"] = 5
    prompt = request.form.get("custom_prompt") or "Generate a useful blog post."
    tone = request.form.get("tone")
    audience = request.form.get("audience")
    length = request.form.get("length") or "750"
    include_image = "include_image" in request.form
    image_style = request.form.get("image_style") or "banner"

    reference_url = request.form.get("reference_url")
    ref_content = ""
    if reference_url:
        try:
            r = requests.get(reference_url)
            ref_content = r.text[:3000]
        except:
            ref_content = ""

    uploaded_file = request.files.get("file")
    if uploaded_file:
        ref_content += uploaded_file.read().decode("utf-8")[:3000]

    system_prompt = f"You are a skilled blog writer. Write in a {tone or 'professional'} tone for an audience of {audience or 'general readers'}. Aim for around {length} words."
    if ref_content:
        system_prompt += f" Use this reference: {ref_content}"

    progress["value"] = 20
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.9
    )

    content = response.choices[0].message.content.strip()
    progress["value"] = 60

    title = content.split("\n")[0].strip("# ")
    body = "\n".join(content.split("\n")[1:])

    image_markdown = ""
    if include_image:
        image_url = get_banner_image(prompt, style=image_style)
        if image_url:
            image_markdown = f"![]({image_url})\n\n"

    final_body = f"# {title}\n\n{image_markdown}{body}"
    filename = save_blog_post(title, final_body, prompt)

    progress["value"] = 100
    return redirect("https://github.com/your-username/your-blog-repo/blob/main/_posts/" + filename)

def get_banner_image(prompt, style="banner"):
    if style == "none":
        return ""
    if "dall" in style.lower():
        dalle_response = client.images.generate(
            model="dall-e-3",
            prompt=f"A {style} style image about: {prompt}",
            size="1024x256",
            quality="standard",
            n=1
        )
        return dalle_response.data[0].url
    else:
        search_term = re.sub(r"[^a-zA-Z0-9 ]", "", prompt).split(" ")[0:5]
        unsplash = f"https://api.unsplash.com/photos/random?query={'-'.join(search_term)}&orientation=landscape&client_id={UNSPLASH_ACCESS_KEY}"
        r = requests.get(unsplash).json()
        return r.get("urls", {}).get("regular", "")

def slugify(text):
    return re.sub(r'[^a-zA-Z0-9-]', '', text.lower().replace(" ", "-")).strip("-")

def save_blog_post(title, content, topic):
    slug = slugify(title)[:80]
    date = datetime.datetime.now().date()
    filename = f"{date}-{slug}.md"
    filepath = os.path.join("_posts", filename)

    post = frontmatter.Post(content, **{
        "title": title,
        "tags": [topic, "ai-generated", "synsera"],
        "date": datetime.datetime.now().isoformat(),
        "topic": topic
    })

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    os.system("git add .")
    os.system(f"git commit -m 'Add new blog post: {title}'")
    os.system("git push")

    return filename

if __name__ == "__main__":
    app.run(debug=True)
