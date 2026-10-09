import os
import sys
import json
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from scraper import fetch_website_links, fetch_website_contents

# 1. Environment Variables and Model Configuration
load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    sys.exit("Error: GEMINI_API_KEY not found. Please check your .env file.")

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
MODEL = "gemini-3.1-flash-lite"

gemini = OpenAI(
    base_url=GEMINI_BASE_URL,
    api_key=api_key
)

# 2. System Prompts
repo_system_prompt = """
You are an expert technical recruiter and software portfolio analyzer.
You are provided with a list of links found on a developer's GitHub profile.

Your job is to identify and extract the repository links that represent actual software projects built by the developer.
Ignore generic GitHub links like followers, following, stars, issues, pull requests, topic pages, or settings.

You should respond strictly in JSON as in this example:
{
    "repositories": [
        {"name": "PetCareAssistant", "url": "https://github.com/developer/PetCareAssistant"},
        {"name": "contacts-app", "url": "https://github.com/developer/contacts-app"}
    ]
}
"""

portfolio_system_prompt = """
You are a senior tech lead and hiring manager.
You analyze raw repository summaries and code descriptions of a software engineer.
Create an executive, impactful Developer Portfolio Summary tailored for tech companies and recruiters.

Your output must be in clean Markdown without code blocks and include:
1. Executive Summary: Core technical profile and specialization areas.
2. Featured Projects: Name of each detected project, inferred tech stack, and key functionalities.
3. Tech Stack Matrix: Categorized breakdown of tools, frameworks, and programming languages demonstrated across the repositories.
4. Engineering Strengths: Observations on their code architecture, modularity, or best practices.
"""


# 3. Stage 1: Smart Repository Filtering Functions
def get_links_user_prompt(url: str) -> str:
    user_prompt = f"""
Here is the list of links found on the GitHub profile {url} -
Please identify and select the relevant links that point to actual software projects and repositories built by the developer.
Respond with the full HTTPS URL in JSON format matching the schema.
Do not include links to generic GitHub pages like followers, following, stars, issues, pull requests, or settings.

Links:
"""
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt


def select_relevant_repos(url: str) -> dict:
    print(f"\n[1/3] Scanning and filtering repositories for: {url}...")
    response = gemini.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": repo_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)


# 4. Bridge: Data Aggregation & Truncation
def fetch_profile_and_all_relevant_repos(url: str) -> str:
    repos_data = select_relevant_repos(url)
    repo_list = repos_data.get("repositories", [])
    
    print(f"[2/3] Found {len(repo_list)} relevant repositories. Fetching contents...")
    result = f"## GitHub Profile URL:\n{url}\n\n## Repositories Analysis:\n"

    for repo in repo_list:
        repo_name = repo.get("name") or repo.get("type", "Repository")
        repo_url = repo["url"]

        print(f"  -> Scraping README and content for '{repo_name}'...")
        result += f"\n\n### Repository: {repo_name}\nURL: {repo_url}\n"

        repo_content = fetch_website_contents(repo_url)
        # Truncate to first 1200 characters per repo to manage token budget
        result += repo_content[:1200]

    return result


def get_portfolio_user_prompt(developer_name: str, url: str) -> str:
    extracted_data = fetch_profile_and_all_relevant_repos(url)
    user_prompt = f"""
You are looking at the software repositories of: {developer_name}
Here is the extracted information from their GitHub profile and project pages:

{extracted_data}
"""
    # Enforce strict 6000-character cap to prevent context window bloat
    return user_prompt[:6000]


# 5. Stage 2: Streaming Portfolio Generation
def stream_portfolio(developer_name: str, url: str):
    print(f"\n[3/3] Generating portfolio analysis ({MODEL} active)...\n")
    print("=" * 60)
    
    user_prompt = get_portfolio_user_prompt(developer_name, url)

    stream = gemini.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": portfolio_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        stream=True
    )

    # Stream tokens in real time with typewriter effect
    for chunk in stream:
        content = chunk.choices[0].delta.content or ""
        print(content, end="", flush=True)

    print("\n" + "=" * 60)
    print("\nAnalysis completed successfully.")


# 6. Command Line Interface (CLI Entrypoint)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub Portfolio & Tech Stack Analyzer")
    parser.add_argument("--username", type=str, default="klkskerem", help="Target GitHub username to analyze")
    parser.add_argument("--name", type=str, default="Kerem", help="Developer's full or preferred name")
    
    args = parser.parse_args()
    
    profile_url = f"https://github.com/{args.username}?tab=repositories"
    stream_portfolio(developer_name=args.name, url=profile_url)