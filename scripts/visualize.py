"""
GitHub Repository Sentiment Analyzer - Step 4: Visualization
-----------------------------------------------------------------
This script reads the sentiment results from Step 3 and creates
two charts:
  1. A pie chart showing the overall Positive/Negative/Neutral split
  2. A bar chart showing average sentiment score over time (by month)

Charts are saved as images in outputs/charts/.

Usage (run from the project root folder):
    python scripts/4_visualize.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------
# STEP A: Load the sentiment data
# ---------------------------------------------------
repo_name = input("Enter the repo name you ran sentiment analysis for (e.g., axios): ").strip()

sentiment_file = os.path.join("data", "processed", f"{repo_name}_issues_sentiment.csv")

if not os.path.exists(sentiment_file):
    print(f"ERROR: Could not find '{sentiment_file}'. Did you run 3_sentiment_analysis.py first?")
    exit()

df = pd.read_csv(sentiment_file)
print(f"\nLoaded {len(df)} rows from '{sentiment_file}'")

# Make sure the output folder exists
chart_dir = os.path.join("outputs", "charts")
os.makedirs(chart_dir, exist_ok=True)

# ---------------------------------------------------
# STEP B: Pie chart - overall sentiment distribution
# ---------------------------------------------------
label_counts = df["sentiment_label"].value_counts()

colors = {"Positive": "#4CAF50", "Negative": "#F44336", "Neutral": "#9E9E9E"}
pie_colors = [colors.get(label, "#2196F3") for label in label_counts.index]

plt.figure(figsize=(6, 6))
plt.pie(
    label_counts.values,
    labels=label_counts.index,
    autopct="%1.1f%%",
    colors=pie_colors,
    startangle=90
)
plt.title(f"Sentiment Distribution - {repo_name}")
plt.tight_layout()

pie_path = os.path.join(chart_dir, f"{repo_name}_sentiment_pie.png")
plt.savefig(pie_path)
plt.close()
print(f"Saved pie chart to '{pie_path}'")

# ---------------------------------------------------
# STEP C: Line chart - average sentiment over time (by month)
# ---------------------------------------------------
df["created_at"] = pd.to_datetime(df["created_at"])
df["month"] = df["created_at"].dt.to_period("M").astype(str)

monthly_avg = df.groupby("month")["sentiment_score"].mean().reset_index()

plt.figure(figsize=(10, 5))
plt.plot(monthly_avg["month"], monthly_avg["sentiment_score"], marker="o", color="#2196F3")
plt.axhline(0, color="gray", linestyle="--", linewidth=1)  # zero line for reference
plt.title(f"Average Sentiment Over Time - {repo_name}")
plt.xlabel("Month")
plt.ylabel("Average Sentiment Score")
plt.xticks(rotation=45)
plt.tight_layout()

trend_path = os.path.join(chart_dir, f"{repo_name}_sentiment_trend.png")
plt.savefig(trend_path)
plt.close()
print(f"Saved trend chart to '{trend_path}'")

print("\nDone! Check the outputs/charts/ folder for your images.")