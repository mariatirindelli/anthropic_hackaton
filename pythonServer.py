from flask import Flask, render_template_string, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import utils

app = Flask(__name__)

COLORS = ["#ffffff", "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF", "#BDB2FF", "#FFC6FF"]

call_number = 0
transcript_windows = []
colored_transcript = []
paragraph_index = 0
paragraph_lists = []

def process_paragraph(par):
    """
    Process a paragraph, check for fallacies and saves the result into a dict

    Parameters
    ----------
    par : str
        The paragraph to be processed.

    Returns
    -------
    dict
        A dictionary containing the processed data, including the paragraph text, fallacy label, and fallacy details.
    """
    res = dict()
    has_fallacy, response = utils.check_for_fallacies(par)
    res["text"] = par
    res["label"] = has_fallacy
    res["fallacy"] = response
    return res

@app.route('/')
def index():
    """
    Render the index.html template.

    Returns
    -------
    str
        The rendered template content.
    """
    html_template = open("index.html", "r").read()
    return render_template_string(html_template)

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    """
    Handle the '/get_transcript' route for POST requests and process the video transcript.

    Returns
    -------
    dict
        A JSON response containing the processed transcript data or an error message if an exception occurs.
    """
    global call_number
    global transcript_windows
    global colored_transcript
    global paragraph_index
    global paragraph_lists
    data = request.get_json()
    video_url = data['video_url']

    try:
        if call_number == 0: 
            transcript = utils.download_transcript(video_url)
            if (transcript is None):
                return jsonify({"error": "Invalid YouTube video URL."})
            
            transcript_windows = utils.create_sliding_windows(transcript, 100)
        
        if (call_number < len(transcript_windows) and paragraph_index>=len(paragraph_lists)):
            paragraphs = utils.divide_in_paragraphs(transcript_windows[call_number], antropic_instance = None)
            paragraph_lists.extend(paragraphs)

        call_number += 1

        if (paragraph_index) >= len(paragraph_lists):
            call_number = 0
            paragraph_index = 0
            paragraph_lists = []
            transcript_windows = []
            colored_transcript=[]
            return jsonify({"completed": "True"})

        entry = process_paragraph(paragraph_lists[paragraph_index])
        entry['color'] = COLORS[entry["label"] % len(COLORS)]  # Cycle through the COLORS array
        paragraph_index += 1

        colored_transcript.append(entry)
        
        return jsonify(colored_transcript)
    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video."})
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
