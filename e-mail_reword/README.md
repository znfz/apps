# E-mail Reworder - README
# Overview

This is a simple command-line tool that takes the contents of an email from a local text file and returns a concise, professional rewrite. The tool reads from initial_email.txt, sends the content to a model via a gateway client, prints the reworded email to the console, and saves it to final_email.txt.

# Key Components

- main.py: CLI entry point that reads initial_email.txt, calls the rewording function, prints the result, and writes final_email.txt.
- utils/summarize.py: Builds prompts for email rewording and calls the model to generate the rewrite.
- utils/client.py: Initializes the Azure OpenAI-compatible client through a gateway and retrieves an access token.
- run.sh: Convenience script for running in a Conda environment.
- requirements.txt: Python dependencies.
- initial_email.txt: Input file containing the original email text.
- final_email.txt: Output file containing the reworded email; overwritten on each run.

# Project Structure
e-mail_reword/
├─ initial_email.txt
├─ final_email.txt
├─ main.py
├─ requirements.txt
├─ README.md
├─ run.sh
└─ utils/
   ├─ client.py
   ├─ summarize.py
   └─ __pycache__/
   
# How It Works

- main.py reads the full content of initial_email.txt.
- utils/summarize.py constructs a system prompt that instructs the model to make emails concise and professional, and a user prompt that wraps your email text.
- The model is called via client.chat.completions.create with model gpt-4o and an authorization token header.
- The result is printed to the terminal and saved to final_email.txt, ensuring the file ends with a newline.
   
# Prerequisites

A working Conda installation.
Python 3.11.
Access to the gateway and model configured in utils/client.py, including a valid access token.   
   
# Setup

1. Clone the repository
   - Clone the entire repository into your working directory.

2. Create and activate a Conda environment   
   - conda create -n air_api python=3.11 -y
   - conda activate air_api
   - pip install -r requirements.txt

3. Create a .env file in the project root with the following information
   - base_url
   - api_version
   - access_token
   
4. Running in bash
   - bash run.sh
