# Brochure Generator

## **Overview**
This is a command-line tool that scrapes a company’s website (landing page plus relevant internal pages) and generates a short, compelling brochure for prospective employees in the USA. It uses a two-step model workflow:
- A link-selection model analyzes the links on the provided URL and chooses only those relevant for a company brochure (ignoring job postings, Terms, Privacy, and email links).
- A writing model turns the collected content into a concise markdown brochure highlighting the company’s science, culture, and benefits.

## **Key Components**
- main.py: CLI entry point. Prompts for the company name and a careers/homepage URL, orchestrates scraping and model calls, and writes the brochure to the product directory.
- utils/web_scraper.py:  
  - fetch_website_contents(url): Extracts text from a page, removing scripts/styles/images/inputs; content is truncated to a sensible limit (20,000 characters).  
  - fetch_website_links(url): Returns all hrefs on the page.
- utils/client.py: Initializes an Azure OpenAI–compatible client through a gateway and retrieves an access token from environment variables. Adds the required authorization header for requests.
- product/: Output directory (created automatically) where the generated brochure file is saved as product/brochure.
- run.sh: Convenience script for running the tool in a Conda environment (if you use Conda).
- requirements.txt: Python dependencies.

## **Project Structure**
brochure/

├─ main.py

├─ requirements.txt

├─ README.md

├─ run.sh

├─ product/                 # Created automatically on first run

└─ utils/

├─ client.py

├─ web_scraper.py

└─ pycache/
   
## **How It Works**
1. You launch the CLI and provide:
   - Company name (optional, used for context)
   - A company careers page or homepage URL (required)
2. The tool scrapes the landing page’s visible text.
3. The link-selection model ("gpt-5" by default in code) receives the discovered links from the landing page and returns only the links it deems relevant for a brochure (excluding job postings, Terms/Privacy, and email links). It is instructed to output fully qualified https URLs in JSON.
4. The tool fetches the text from each selected link and compiles a single content bundle.
5. The brochure-writing model ("gpt-4.1-mini" by default in code) receives the bundle and produces a short markdown brochure highlighting science, company culture, and benefits.
6. The brochure is saved to product/brochure (no extension by default).
   
Prerequisites

A working Conda installation.
Python 3.11.
Access to the gateway and model configured in utils/client.py, including a valid access token.   
   
Setup

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
