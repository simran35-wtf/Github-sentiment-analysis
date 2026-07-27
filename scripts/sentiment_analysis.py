"""
GitHub Repository Sentiment Analyzer - Step 3: Sentiment Analysis
-----------------------------------------------------------------
This script reads the cleaned CSV from Step 2, runs sentiment
analysis on each entry using VADER (a well-known lexicon-based
sentiment tool, similar in spirit to the dictionary approach you
learned in class), and saves the results with sentiment scores
and labels to data/processed/.

Usage (run from the project root folder):
    python scripts/3_sentiment_analysis.py
"""

import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------
# STEP A: Load the cleaned data
# ---------------------------------------------------
repo_name = input("Enter the repo name you cleaned data for (e.g., axios): ").strip()

clean_file = os.path.join("data", "processed", f"{repo_name}_issues_clean.csv")

if not os.path.exists(clean_file):
    print(f"ERROR: Could not find '{clean_file}'. Did you run 2_data_cleaner.py first?")
    exit()

df = pd.read_csv(clean_file)
print(f"\nLoaded {len(df)} rows from '{clean_file}'")

# ---------------------------------------------------
# STEP B: Set up VADER sentiment analyzer
# ---------------------------------------------------
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if pd.isna(text) or str(text).strip() == "":
        return 0.0, "Neutral"

    scores = analyzer.polarity_scores(str(text))
    compound = scores["compound"]   # overall score from -1 (very negative) to +1 (very positive)

    # Standard VADER thresholds for labeling
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return compound, label

# ---------------------------------------------------
# STEP C: Apply sentiment analysis to every row
# ---------------------------------------------------
print("\nRunning sentiment analysis...")

results = df["clean_text"].apply(get_sentiment)
df["sentiment_score"] = results.apply(lambda x: x[0])
df["sentiment_label"] = results.apply(lambda x: x[1])

# ---------------------------------------------------
# STEP D: Print a quick summary
# ---------------------------------------------------
print("\nSentiment distribution:")
print(df["sentiment_label"].value_counts())

avg_score = df["sentiment_score"].mean()
print(f"\nAverage sentiment score: {avg_score:.3f} "
      f"({'overall positive tone' if avg_score > 0 else 'overall negative tone' if avg_score < 0 else 'neutral overall'})")

# ---------------------------------------------------
# STEP E: Save the results
# ---------------------------------------------------
output_file = os.path.join("data", "processed", f"{repo_name}_issues_sentiment.csv")
df.to_csv(output_file, index=False)

print(f"\nDone! Sentiment results saved to '{output_file}'")
print("Next step: visualize the results (4_visualize.py).")