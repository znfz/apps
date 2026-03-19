Ask and Speak - README
Overview

Ask and Speak is a simple Gradio web app that answers your question with OpenAI Chat Completions, then speaks the answer using Text-to-Speech. You can choose chat and TTS models, voice, and audio format. The app maintains an in-memory chat history per session and plays the generated audio automatically.

Key Components

main.py: Builds the Gradio UI, handles chat + TTS, and manages session history.
utils/client.py: Provides get_client to initialize the OpenAI Python client using environment variables.
run.sh: Convenience script for launching the app.
requirements.txt: Python dependencies.
README.md: Project documentation.

Project Structure

audio_chatbot/
├─ main.py
├─ requirements.txt
├─ README.md
├─ run.sh
└─ utils/
   ├─ client.py
   
How It Works:

Compose messages
The app builds a messages list with a system prompt, prior history, and your latest question.
Get the text answer
It calls:
client.chat.completions.create with:
model: selectable (default "gpt-4o-mini")
messages: system + history + user
Synthesize speech
It streams TTS audio to a temporary file using:
client.audio.speech.with_streaming_response.create with:
model: selectable (default "gpt-4o-mini-tts")
voice: selectable (default "alloy")
input: assistant’s text answer
Play and update history
Gradio displays the text answer and plays the audio file. The in-memory history is updated. A Clear button resets the state.
UI Features
Question: Type your question.
Chat model: Choose from "gpt-4o-mini", "gpt-4o", "gpt-4o-mini-high".
TTS model: Choose from "gpt-4o-mini-tts", "gpt-4o-tts".
Voice: Choose "alloy", "verse", "aria", or "sage".
Audio format: Choose "wav", "mp3", or "ogg".
System prompt: Customize assistant behavior.
Share link: The app launches with share=True to provide a public Gradio link.
   
Prerequisites
Python 3.11+
An OpenAI API key
   
Setup
Clone the repository

Clone this repo into your working directory.
Create and activate an environment

Using Conda:

conda create -n air_api python=3.11 -y
conda activate air_api
Or using venv:

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
Install dependencies


pip install -r requirements.txt
Create a .env file in the project root


OPENAI_API_KEY=your_openai_api_key_here
Run the app

Using the script:

bash run.sh
Or directly:

python main.py