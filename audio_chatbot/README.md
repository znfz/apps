# Ask and Speak - README
## Overview

Ask and Speak is a simple Gradio web app that answers your question with OpenAI Chat Completions, then speaks the answer using Text-to-Speech. You can choose chat and TTS models, voice, and audio format. The app maintains an in-memory chat history per session and plays the generated audio automatically.

## Key Components

- main.py: Builds the Gradio UI, handles chat + TTS, and manages session history.
- utils/client.py: Provides get_client to initialize the OpenAI Python client using environment variables.
- run.sh: Convenience script for launching the app.
- requirements.txt: Python dependencies.
- README.md: Project documentation.

## Project Structure
audio_chatbot/

├─ main.py

├─ requirements.txt

├─ README.md

├─ run.sh

└─ utils/

   ├─ client.py
   
## How It Works:

1. Build the message payload
   - The app composes a messages list from the system prompt, prior chat history, and your latest question.
2. Get the text answer
   - It calls client.chat.completions.create with:
   - model: selectable (default: gpt-4o-mini)
   - messages: system + history + user
3. Synthesize speech
   - It streams TTS audio to a temporary file via client.audio.speech.with_streaming_response.create with:
   - model: selectable (default: gpt-4o-mini-tts)
   - voice: selectable (default: alloy)
   - input: the assistant’s text answer
4. Play and update history
   - Gradio displays the text response, plays the generated audio, and appends the exchange to the in-memory history.
5. Reset when needed
   - A Clear button wipes the in-memory state. The app launches with share=True to generate a public Gradio link
   
## Prerequisites
- Python 3.11+
- An OpenAI API key
   
## Setup

1. Clone the repository
   - Clone the entire repository into your working directory.

2. Create and activate a Conda environment   
   - conda create -n air_api python=3.11 -y
   - conda activate air_api
   - pip install -r requirements.txt

3. Create a .env file in the project root with the following information
   - OPENAI_API_TOKEN
   
4. Running in bash
   - bash run.sh

