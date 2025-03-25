from flask import Flask, request, render_template, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import os
import re
import requests
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# 🔹 Configure Google AI API (Get API Key from Google AI Studio)
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# 🔹 Function to Extract Clean Subtitles

def extract_subtitles(vtt_file):
    if not os.path.exists(vtt_file):
        return None

    with open(vtt_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    clean_subs = []
    seen_lines = set()

    for idx, line in enumerate(lines):
        #print(f"DEBUG Line #{idx}: {repr(line)}")  # <-- Print raw line
        if "-->" in line or line.strip() == "":
           # print("SKIPPED line: (timestamp or blank)")
            continue

        clean_line = re.sub(r"<.*?>", "", line.strip())
        if clean_line and clean_line not in seen_lines:
           # print("KEPT line:", repr(clean_line))
            clean_subs.append(clean_line)
            seen_lines.add(clean_line)

    full_transcript = " ".join(clean_subs)
    # print("DEBUG final transcript:", repr(full_transcript[:500]))
    return full_transcript

   # print("DEBUG Transcript:", transcript[:500])

# 🔹 Function to Summarize Text Using AI
def generate_summary(transcript):
    model = genai.GenerativeModel("gemini-2.0-flash-lite")

    prompt = f"""analyze the content and give a star rating out of 5 and tell me what is being told as summary plz dont miss the important information while making summary in this YouTube transcript using markdown formatting, with bullet points, headings if needed, and bold text where relevant:

{transcript}
"""

    response = model.generate_content(contents=[prompt])
    #print("DEBUG AI Response:", response)

    # Handle content safely
    try:
        markdown_response = response.text.strip()
        return markdown_response
    except Exception as e:
       # print("Error parsing AI response:", e)
        return "⚠️ Error generating summary."
 

# 🔹 API to Fetch Subtitle and Generate Summary
@app.route('/summary', methods=['POST'])
def get_summary():
    data = request.json
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    ydl_opts = {
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
        "subtitlesformat": "vtt",
        "outtmpl": "subtitles.%(ext)s"
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            video_title = info.get("title", "Unknown Title")
            subtitles = info.get('requested_subtitles', {})

            if 'en' in subtitles:
                subtitle_file = subtitles['en']['filepath']
                transcript = extract_subtitles(subtitle_file)

                if transcript:
                    summary_markdown = generate_summary(transcript)

                    return jsonify({
                        "title": video_title,
                        #"clickbait_score": 3,  # TODO: Add clickbait detection logic
                        "summary_markdown": summary_markdown
                    })

            return jsonify({"error": "No English subtitles found."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    return "✅ YT Summary 1.3 is running!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

    app.run(host='0.0.0.0', port=10000)
