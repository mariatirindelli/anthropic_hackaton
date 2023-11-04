from flask import Flask, render_template_string, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
import random
import utils

app = Flask(__name__)



def ANTRHOPIC_PLACEHOLDER(transcript):
    """
    with 10% probability label each line with a non-zero label

    each label later will correspond to a logical fallacy on the backend
     and a different color on the frontend
    """
    paragraphs = utils.divide_in_paragraphs(transcript, antropic_instance = None)
    paragraph_lists.extend(paragraphs)
    
    has_fallacy, response = utils.check_for_fallacies(paragraph_lists[paragraph_index])
    
    
    res = []
    
    
    print(len(paragraphs))
    for par in paragraphs:
        print("Processing par")
        has_fallacy, response = utils.check_for_fallacies(transcript)
        print("Processed par")
        current_res = dict()
        current_res["text"] = par
        current_res["label"] = has_fallacy
        
        res.append(current_res)
    
    print("Finished processing")
    return res

def process_paragraph(par):
    
    res = dict()
    has_fallacy, response = utils.check_for_fallacies(par)
    res["text"] = par
    res["label"] = has_fallacy
    res["fallacy"] = response
    return res

@app.route('/')
def index():
    html_template = open("index.html", "r").read()
    return render_template_string(html_template)

FALLACIES = [
    "No Fallacy",
    "Ad Hominem",
    "Appeal to Authority",
    "Appeal to Belief",
    "Appeal to Common Practice",
    "Appeal to Consequences of a Belief",
    "Appeal to Emotion",
    "Appeal to Fear",
    "Appeal to Flattery",
]
COLORS = ["#ffffff", "#FFADAD", "#FFD6A5", "#FDFFB6", "#CAFFBF", "#9BF6FF", "#A0C4FF", "#BDB2FF", "#FFC6FF"]

call_number = 0
transcript_windows = []
colored_transcript = []
paragraph_index = 0
paragraph_lists = []

def process_nex_window():
    global call_number
    global transcript_windows
    print("Processing window: ", call_number)

def get_random_par():
    res = dict()
    has_fallacy, response = 1, "bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla v bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla"
    res["text"] = "bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla v bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla"
    res["label"] = has_fallacy
    res["fallacy"] = response
    return res

@app.route('/get_transcript', methods=['POST'])
def get_transcript():
    global call_number
    global transcript_windows
    global colored_transcript
    global paragraph_index
    global paragraph_lists
    data = request.get_json()
    video_url = data['video_url']
    # Extract video ID from URL
    video_id = ''
    try:
        #if call_number == -1: 
            #res_rand = [get_random_par()]
            #call_number += 1
            #return jsonify(res_rand)
        if call_number == 0: 
            transcript = utils.download_transcript(video_url)
            if (transcript is None):
                return jsonify({"error": "Invalid YouTube video URL."})
            
            transcript_windows = utils.create_sliding_windows(transcript, 100)
        
        #if (call_number >= len(transcript_windows)):
            #return jsonify({"completed": "True"})
        if (call_number <= len(transcript_windows) and paragraph_index>=len(paragraph_lists)):
            #current_window = ANTRHOPIC_PLACEHOLDER(transcript_windows[call_number])
            paragraphs = utils.divide_in_paragraphs(transcript_windows[call_number], antropic_instance = None)
            paragraph_lists.extend(paragraphs)

        call_number += 1

        if (paragraph_index) >= len(paragraph_lists):
            return jsonify({"completed": "True"})

        entry = process_paragraph(paragraph_lists[paragraph_index])
        entry['color'] = COLORS[entry["label"] % len(COLORS)]  # Cycle through the COLORS array
        paragraph_index += 1
        print(call_number)

        #for index, entry in enumerate(current_paragraphs):
           # entry['color'] = COLORS[entry["label"] % len(COLORS)]  # Cycle through the COLORS array
            #entry['fallacy'] = FALLACIES[entry["label"] % len(FALLACIES)]

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
