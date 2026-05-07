from flask import Flask, render_template, request
from youtube_transcript_api import YouTubeTranscriptApi
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re

app = Flask(__name__)

# Extract YouTube video ID
def extract_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

@app.route("/", methods=["GET", "POST"])
def home():
    summary = ""
    error = ""

    if request.method == "POST":
        url = request.form.get("url")
        video_id = extract_video_id(url)

        if not video_id:
            error = "Invalid YouTube URL"
            return render_template("index.html", error=error)

        try:
            # Fetch transcript
            transcript = YouTubeTranscriptApi().fetch(video_id)

            # Convert transcript to text
            text = " ".join([item.text for item in transcript])

            # Limit text size
            text = text[:3000]

            # Summarize text
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summarizer = LsaSummarizer()

            summary_sentences = summarizer(parser.document, 5)
            summary = " ".join(str(sentence) for sentence in summary_sentences)

        except Exception as e:
            error = f"Error: {str(e)}"

    return render_template("index.html", summary=summary, error=error)

if __name__ == "__main__":
    app.run(debug=True)