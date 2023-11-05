from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from youtube_transcript_api import YouTubeTranscriptApi

# Function to download and save the transcript with timestamps
def download_transcript(youtube_url):
    """
    Download the transcript with timestamps for a YouTube video.

    Parameters
    ----------
    youtube_url : str
        The URL of the YouTube video.

    Returns
    -------
    dict or None
        A dictionary containing the transcript with timestamps or None if an error occurs during the download process.
    """
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
    """
    Save the raw transcript with timestamps to a file.

    Parameters
    ----------
    transcript_with_timestamps : dict
        A dictionary containing the transcript with timestamps.
    out_file : str
        The name of the output file.

    Returns
    -------
    None
    """
    raw_text = " ".join([transcript_with_timestamps[timestamp] for timestamp in transcript_with_timestamps.keys()])
    with open(out_file, 'w') as fid:
        fid.write(raw_text)

def create_sliding_windows(transcript_with_timestamps, window_size):
    """
    transcript: dictionary with timestamps as keys and text as values
    window_size: number of lines to include in each window
    """
    transcript_list = [transcript_with_timestamps[timestamp] for timestamp in transcript_with_timestamps.keys()]
    transcript_chunks = [transcript_list[i:i + window_size] for i in range(0, len(transcript_list), window_size)]
    windows = [" ".join(item) for item in transcript_chunks]

    return windows

def divide_in_paragraphs(raw_input, antropic_instance = None):
    """
    Divide the transcript with timestamps into sliding windows.

    Parameters
    ----------
    transcript_with_timestamps : dict
        A dictionary containing the transcript with timestamps.
    window_size : int
        The number of lines to include in each window.

    Returns
    -------
    list
        A list of strings representing the sliding windows of the transcript.
    """
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

    first_word_idx = text_paragraphs.find("\n")
    text_paragraphs = text_paragraphs[first_word_idx::]

    processed_paragraphs = text_paragraphs.split("\n\n")
    return [item for item in processed_paragraphs if len(item)>3]

def check_for_fallacies(chunk_text, antropic_instance = None):
    """
    Check for logical fallacies in the chunk text.

    Parameters
    ----------
    chunk_text : str
        The text to be checked for logical fallacies.
    antropic_instance : Anthropic, optional
        An instance of the Anthropic API, by default None.

    Returns
    -------
    tuple
        A tuple containing a binary value indicating the presence of fallacies and the text with fallacy details.
    """
    
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