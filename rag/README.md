## Expert Assistant (RAG) — Gradio + LangChain + Chroma

# Overview

A lightweight Retrieval-Augmented Generation app that converts PDFs to Markdown, chunks and embeds content with OpenAI, stores vectors in Chroma, and answers questions via a Gradio chat UI using GPT-4.1-nano.

# Key Features

PDF to Markdown conversion via MarkItDown
Robust text chunking with overlap for better recall
OpenAI embeddings (text-embedding-3-large) persisted in Chroma
Chat interface powered by Gradio with retrieved context display
Simple RAG pipeline with conversation history-aware retrieval

# Project Structure

- app.py
- README.md
- run.sh
- files_pdf/
- files_md/
- vector_db/
- utils/
  - ingest.py
  - answer.py
  - pycache/
  
# Roles

- app.py: Gradio UI, calls answer_question and displays retrieved context
- utils/ingest.py: Converts PDFs to Markdown, splits, embeds, and builds Chroma DB
- utils/answer.py: Retrieval and LLM answering logic (RAG)
- files_pdf: Place your source PDFs here
- files_md: Auto-generated Markdown from PDFs (or add your own .md)
- vector_db: Chroma persistent store (auto-created)
   
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
   
# Prerequisites
- Python 3.11+
- An OpenAI API key
   
# Setup
- Clone the repository

Clone this repo into your working directory.
Create and activate an environment

# Using Conda:
- conda create -n llms python=3.11 -y
- conda activate llms
- pip install -r requirements.txt

# Create a .env file in the project root
- OPENAI_API_KEY="xxxxxxxxxxxxxxxx"

# Run the app
- bash run.sh
