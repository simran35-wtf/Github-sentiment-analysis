"""
GitHub Repository Sentiment Analyzer - Step 1: Data Collection
-----------------------------------------------------------------
This script fetches issues from a specified GitHub repository and
saves them as a CSV file in the data/raw/ directory. This raw data
will be used for text cleaning and sentiment analysis in later steps.

Usage (run from the project root folder):
    python scripts/1_data_collector.py
"""

import os
import requests
import pandas as pd
import time
from dotenv import load_dotenv

# ---------------------------------------------------
# STEP A: Load GitHub token from .env file
# ---------------------------------------------------
load_dotenv()  # Loads environment variables defined in the .env file

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("ERROR: GITHUB_TOKEN not found. Please check that your .env file "
          "contains a line like GITHUB_TOKEN=your_token_here")
    exit()

# ---------------------------------------------------
# STEP B: Get target repository from user
# ---------------------------------------------------
repo_full_name = input("Enter the repository name (e.g., axios/axios or facebook/react): ").strip()
owner, repo = repo_full_name.split("/")

MAX_PAGES = 10      # Number of pages to fetch (each page ~30 issues)
PER_PAGE = 30

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BASE_URL = f"https://api.github.com/repos/{owner}/{repo}/issues"

# ---------------------------------------------------
# STEP C: Fetch issues from the GitHub API
# ---------------------------------------------------
all_data = []

print(f"\nFetching data from '{repo_full_name}'...\n")

for page in range(1, MAX_PAGES + 1):
    params = {
        "state": "all",         # Fetch both open and closed issues
        "per_page": PER_PAGE,
        "page": page,
        "sort": "created",
        "direction": "desc"     # Most recent issues first
    }

    response = requests.get(BASE_URL, headers=HEADERS, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.json().get('message')}")
        break

    issues = response.json()

    if not issues:
        print("No more issues found. Stopping.")
        break

    for issue in issues:
        # The GitHub "issues" endpoint also returns pull requests,
        # so we filter those out to keep only actual issues.
        if "pull_request" in issue:
            continue

        all_data.append({
            "type": "issue_body",
            "issue_number": issue["number"],
            "author": issue["user"]["login"],
            "author_type": issue["user"]["type"],   # "User" or "Bot"
            "created_at": issue["created_at"],
            "state": issue["state"],
            "title": issue["title"],
            "text": issue["body"] if issue["body"] else "",
        })

    print(f"Page {page} complete - {len(all_data)} entries collected so far")
    time.sleep(0.5)  # Small delay to stay within API rate limits

# ---------------------------------------------------
# STEP D: Save the collected data as a CSV file
# ---------------------------------------------------
df = pd.DataFrame(all_data)

# Build the path to the data/raw/ folder relative to the project root
output_dir = os.path.join("data", "raw")
os.makedirs(output_dir, exist_ok=True)  # Create the folder if it doesn't exist

output_file = os.path.join(output_dir, f"{repo}_issues_raw.csv")
df.to_csv(output_file, index=False)

print(f"\nDone! {len(df)} issues saved to '{output_file}'")
print("Next step: clean the text data (2_data_cleaner.py).")