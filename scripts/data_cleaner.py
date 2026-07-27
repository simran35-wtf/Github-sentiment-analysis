"""
GitHub Repository Sentiment Analyzer - Step 2: Data Cleaning
-----------------------------------------------------------------
This script reads the raw CSV generated in Step 1, cleans the text
(removes code blocks, links, markdown formatting, bot entries, and
empty text), and saves a cleaned CSV to data/processed/.

Usage (run from the project root folder):
    python scripts/2_data_cleaner.py
"""

import os
import re
import pandas as pd

# ---------------------------------------------------
# STEP A: Ask which raw file to clean
# ---------------------------------------------------
repo_name = input("Enter the repo name you collected data for (e.g., axios): ").strip()

raw_file = os.path.join("data", "raw", f"{repo_name}_issues_raw.csv")

if not os.path.exists(raw_file):
    print(f"ERROR: Could not find '{raw_file}'. Did you run data_collector.py first?")
    exit()

df = pd.read_csv(raw_file)
print(f"\nLoaded {len(df)} rows from '{raw_file}'")

# ---------------------------------------------------
# STEP B: Define a text-cleaning function
# ---------------------------------------------------
def clean_text(text):
    if pd.isna(text):
        return ""

    text = str(text)

    # Remove code blocks (```...```)
    text = re.sub(r"```[\s\S]*?```", " ", text)

    # Remove inline code (`...`)
    text = re.sub(r"`[^`]*`", " ", text)

    # Remove URLs
    text = re.sub(r"http\S+|www\.\S+", " ", text)

    # Remove markdown headers, bold/italic symbols
    text = re.sub(r"[#*_>~]", " ", text)

    # Remove HTML tags if any
    text = re.sub(r"<[^>]+>", " ", text)

    # Collapse multiple spaces/newlines into one space
    text = re.sub(r"\s+", " ", text).strip()

    return text

# ---------------------------------------------------
# STEP C: Apply cleaning
# ---------------------------------------------------
df["clean_text"] = df["text"].apply(clean_text)

# ---------------------------------------------------
# STEP D: Filter out unwanted rows
# ---------------------------------------------------
before_count = len(df)

# Remove rows where author looks like a bot
df = df[~df["author"].str.contains("bot", case=False, na=False)]
df = df[df["author_type"].str.lower() != "bot"]

# Remove rows with empty cleaned text
df = df[df["clean_text"].str.strip() != ""]

after_count = len(df)
print(f"Removed {before_count - after_count} rows (bots / empty text)")
print(f"{after_count} rows remain after cleaning")

# ---------------------------------------------------
# STEP E: Save cleaned data
# ---------------------------------------------------
output_dir = os.path.join("data", "processed")
os.makedirs(output_dir, exist_ok=True)

output_file = os.path.join(output_dir, f"{repo_name}_issues_clean.csv")
df.to_csv(output_file, index=False)

print(f"\nDone! Cleaned data saved to '{output_file}'")
print("Next step: run sentiment analysis (sentiment_analysis.py).")