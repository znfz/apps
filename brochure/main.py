# Generic
import os
from dotenv import load_dotenv
import json
from IPython.display import Markdown, display, update_display
from utils.web_scraper import fetch_website_contents, fetch_website_links
from utils.client import get_client
from pathlib import Path

link_system_prompt = """
You are provided with a list of links found on a company careers webpage.
You are able to decide which of the links would be most relevant to include in a brochure for prospective employees in the USA.
Ignore on links about job postings.
You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
"""

def get_links_user_prompt(url):
    user_prompt = f"""
Here is the list of links on the website {url} -
Please decide which of these are relevant web links for a brochure about the company, 
respond with the full https URL in JSON format.
Do not include Terms of Service, Privacy, email links.

Links (some might be relative links):

"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt

def select_relevant_links(url):
    print(f"Selecting relevant links for {url}")
    client = get_client()
    response = client.chat.completions.create(
        model='gpt-5',
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    links = json.loads(result)
    print(f"Found {len(links['links'])} relevant links")
    return links

# main.py
from urllib.parse import urlparse

def fetch_page_and_all_relevant_links(url):
    contents = fetch_website_contents(url)
    relevant_links = select_relevant_links(url)
    base_host = urlparse(url).netloc

    result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"
    for link in relevant_links['links']:
        link_url = link["url"]
        if urlparse(link_url).netloc != base_host:
            print(f"Skipping off-domain link: {link_url}")
            continue
        result += f"\n\n### Link: {link['type']}\n"
        result += fetch_website_contents(link_url)
    return result


brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective employees that would entice them to join the company.
Respond in markdown without code blocks.
Include details of  the science, company culture, benefits.
"""

def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
You are looking at a company called: {company_name}
Here are the contents of its landing page and other relevant pages;
use this information to build a short brochure of the company in markdown without code blocks.\n\n
"""
    user_prompt += fetch_page_and_all_relevant_links(url)
    return user_prompt

def create_brochure(company_name, url, output_dir="product"):
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
    )
    result = response.choices[0].message.content

    # Ensure 'product' directory exists and save as 'brochure' (no extension)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / "brochure"  # use "brochure.md" if you prefer an extension
    file_path.write_text(result, encoding="utf-8")
    print(f"Brochure saved to: {file_path.resolve()}")
    
    
def main():
    print("=== Company Brochure Builder ===")
    company = input("Enter the company name: ").strip()
    url = input("Enter the company careers or homepage URL: ").strip()

    if not url:
        print("A valid URL is required to proceed.")
        return

    if not company:
        company = "Unknown Company"

    # Save results into ./product directory
    create_brochure(company, url, output_dir="product")

if __name__ == "__main__":
    main()