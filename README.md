# ArguMend

The application automatically fetches captions from you tube videos based on the video url. The application then cleans up the transcript to divide into coherent paragraphs and correct minor grammar mistakes. It then runs logical fallacy detector using claude APIs on the processed text, and displays it highlighting them in red if any fallacy was detected. The application furhter displays an explanation of the detected fallacy to inform the user. 

The application is structured as follows: 
- html/css front-end UI. The UI is composed of a text field where the URL of the youtube video can be pasted, and a push button.
<p align="center">
  <kbd>
    <img src="/doc_images/pic0.png" alt="Image Alt Text" width="600" style="border: 2px solid black;" />
  </kbd>
</p>

- Clicks of the button triggers a POST request to the get_transcript function to be send to the server, passing the url as an input and expecting the processed transcript as a response.
- The backend is a python-based server. The server defines the "get_transcript" method. Within the method, the function first downloads the youtube transcripts if not yet available, and splits them into chunks. It then proceeds to take the next available chunk, and utilizes claude APIs to correct gramatical/transcription mistakes in the text, and divides it into paragraphs. The function then process the next paragraph and uses claude APIs to identify fallacies. The model is prompted to identify if any fallacy can be identified and to provide a short explanation of the kind of fallacy and the reason for its detection in the text. The function finally returns a list of the available paragraphs, where each item contains the paragraph text, a boolean value identifying the presence of fallacies and a free text containing the fallacy description.
- Upon reception of the get_transcript response, at a front-end level, the cleaned-up and received paragraphs are displayed on the UI. Paragraphs where a fallacy is detected are highlighted in red:
<p align="center">
  <kbd>
    <img src="/doc_images/pic1.png" alt="Image Alt Text" width="600" style="border: 2px solid black;" />
  </kbd>
</p>

- When highligthed paragraphs are pointed at with the mouse, a pop-up dialog box appears, showing list of the identified fallacies in the text, alongside with their description contextualized with the text:
<p align="center">
  <kbd>
    <img src="/doc_images/pic2.png" alt="Image Alt Text" width="600" style="border: 2px solid black;" />
  </kbd>
</p>
