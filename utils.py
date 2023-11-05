from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from youtube_transcript_api import YouTubeTranscriptApi
import time
import sys
import random

# Function to download and save the transcript with timestamps
def download_transcript(youtube_url):
    # Extract the video ID from the URL
    video_id = youtube_url.split('watch?v=')[-1]

    if ("/shorts/") in youtube_url:
        video_id= youtube_url.split('/shorts/')[-1]
    transcript_with_timestamps = {}
    try:
        # Download the transcript that includes timestamps
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Saving the transcript with timestamps to a file
        for entry in transcript:
            start = entry['start']
            text = entry['text'].replace('\n', ' ')
            # file.write(f"{start} --> {text}\n")
            transcript_with_timestamps[start] = text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return transcript_with_timestamps

def save_raw_file(transcript_with_timestamps, out_file):
    raw_text = " ".join([transcript_with_timestamps[timestamp] for timestamp in transcript_with_timestamps.keys()])
    with open(out_file, 'w') as fid:
        fid.write(raw_text)

# Function to chunk the transcript into sliding windows
def create_sliding_windows(transcript_with_timestamps, window_size):
    """
    transcript: dictionary with timestamps as keys and text as values
    window_size: number of lines to include in each window
    """
    transcript_list = [transcript_with_timestamps[timestamp] for timestamp in transcript_with_timestamps.keys()]
    transcript_chunks = [transcript_list[i:i + window_size] for i in range(0, len(transcript_list), window_size)]
    windows = [" ".join(item) for item in transcript_chunks]

    return windows

def dummy_divide_in_paragraph(raw_input, antropic_instance = None):
    parts = [raw_input[i:i + len(raw_input) // 4] for i in range(0, len(raw_input), len(raw_input) // 4)]
    return parts

def dummy_check_for_fallacies(chunk_text, antropic_instance = None):
    if random.random() < 0.5:
           return 1, "Random Res"
    else:
        return 0, ""
        

def divide_in_paragraphs(raw_input, antropic_instance = None):
    local_instance = antropic_instance is None
    if (local_instance):
        antropic_instance = Anthropic(
        api_key="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",)
    
    #prompt = f"{HUMAN_PROMPT}The following is a transcription of a video, please read and fix minor transcription errors, and divide the transcription into coherent chunks changing the text:\n\n{raw_input}{AI_PROMPT}"
   
    prompt = f"{HUMAN_PROMPT}The following is a transcription of a video, please read and fix minor transcription errors, then discard incomplete sentences in the beginning and the end of the transcription, and divide the transcription into coherent chunks of around 100 words without changing the text:\n\n{raw_input}{AI_PROMPT}"
    response = antropic_instance.completions.create(
        model="claude-2",  # or the latest model available
        max_tokens_to_sample=30000,
        prompt=prompt
    )

    text_paragraphs = response.completion

    if (local_instance):
        antropic_instance.close()


    # Clean up the text to remove the text introduced by the assistant
    first_word_idx = text_paragraphs.find("\n")
    text_paragraphs = text_paragraphs[first_word_idx::]

    processed_paragraphs = text_paragraphs.split("\n\n")
    return [item for item in processed_paragraphs if len(item)>3]

def check_for_fallacies(chunk_text, antropic_instance = None):
    local_instance = antropic_instance is None
    if (local_instance):
        antropic_instance = Anthropic(
        api_key="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",)

    prompt = f"{HUMAN_PROMPT} Identify if there are logical fallacies. If it exists, list the fallacies by bullet point, and explain why that fallacy exists. If there is no fallacy, just say N/A and nothing else: \n\n{chunk_text}{AI_PROMPT}"
    
    response = antropic_instance.completions.create(
        model="claude-2",  # or the latest model available
        max_tokens_to_sample=30000,
        prompt=prompt
    )
    if (local_instance):
        antropic_instance.close()

    has_fallacies = 1
    text = response.completion
    if "N/A" in response.completion or "I do not see" in response.completion:
        has_fallacies = 0
        text=""
    return has_fallacies, text

def divide_in_paragraphs_fun(video_url):
    transcript = download_transcript(video_url)
    windows = create_sliding_windows(transcript, 100)

    paragraphed_text = ""
    for window in windows:
        res = divide_in_paragraphs(window)

        print(window)
        print("-------")
        print(res)
        paragraphed_text += "\n" + res
        #print(paragraphed_text)



if __name__ == '__main__':
    video_url = "https://www.youtube.com/watch?v=855Am6ovK7s"
    divide_in_paragraphs_fun(video_url)


    # app.run(debug=True)