"""
GitHub Repository Sentiment Analyzer - Interactive Dashboard
-----------------------------------------------------------------
An interactive web dashboard built with Streamlit. It lets you:
  1. Browse sentiment results for repos you've already analyzed
     (from data/processed/), OR
  2. Enter any new public GitHub repo and analyze it live.

Usage (run from the project root folder):
    streamlit run app.py
"""

import os
import re
import glob
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------
# Setup
# ---------------------------------------------------
load_dotenv()

# Try to load the token from Streamlit secrets first (used when deployed on
# Streamlit Cloud). If not found, fall back to the local .env file.
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except (KeyError, FileNotFoundError):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

analyzer = SentimentIntensityAnalyzer()

st.set_page_config(page_title="GitHub Sentiment Analyzer", layout="wide")
st.title("📊 GitHub Repository Sentiment Analyzer")
st.caption("Analyze the emotional tone of issue discussions in any public GitHub repository.")


# ---------------------------------------------------
# Helper functions (same logic as scripts 1-3, reused here)
# ---------------------------------------------------
def clean_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = re.sub(r"```[\s\S]*?```", " ", text)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[#*_>~]", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def get_sentiment(text):
    if not text.strip():
        return 0.0, "Neutral"
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"
    return compound, label


@st.cache_data(show_spinner=False)
def fetch_and_analyze(owner, repo, max_pages=10):
    """Fetches issues from GitHub, cleans them, and runs sentiment analysis."""
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    base_url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    all_data = []

    for page in range(1, max_pages + 1):
        params = {"state": "all", "per_page": 30, "page": page,
                  "sort": "created", "direction": "desc"}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code != 200:
            st.error(f"GitHub API error: {response.status_code} - {response.json().get('message')}")
            break

        issues = response.json()
        if not issues:
            break

        for issue in issues:
            if "pull_request" in issue:
                continue
            all_data.append({
                "issue_number": issue["number"],
                "author": issue["user"]["login"],
                "author_type": issue["user"]["type"],
                "created_at": issue["created_at"],
                "state": issue["state"],
                "title": issue["title"],
                "text": issue["body"] if issue["body"] else "",
            })
        time.sleep(0.3)

    df = pd.DataFrame(all_data)
    if df.empty:
        return df

    # Clean
    df["clean_text"] = df["text"].apply(clean_text)
    df = df[~df["author"].str.contains("bot", case=False, na=False)]
    df = df[df["author_type"].str.lower() != "bot"]
    df = df[df["clean_text"].str.strip() != ""]

    # Sentiment
    results = df["clean_text"].apply(get_sentiment)
    df["sentiment_score"] = results.apply(lambda x: x[0])
    df["sentiment_label"] = results.apply(lambda x: x[1])

    return df


def render_dashboard(df, repo_label):
    """Renders charts and tables for a given sentiment dataframe."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Issues Analyzed", len(df))
    col2.metric("Average Sentiment", f"{df['sentiment_score'].mean():.3f}")
    top_label = df["sentiment_label"].value_counts().idxmax()
    col3.metric("Dominant Sentiment", top_label)

    st.subheader(f"Sentiment Distribution - {repo_label}")
    col_pie, col_trend = st.columns(2)

    with col_pie:
        label_counts = df["sentiment_label"].value_counts()
        colors = {"Positive": "#4CAF50", "Negative": "#F44336", "Neutral": "#9E9E9E"}
        pie_colors = [colors.get(l, "#2196F3") for l in label_counts.index]
        fig1, ax1 = plt.subplots()
        ax1.pie(label_counts.values, labels=label_counts.index, autopct="%1.1f%%",
                colors=pie_colors, startangle=90)
        ax1.set_title("Positive vs Negative vs Neutral")
        st.pyplot(fig1)

    with col_trend:
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["month"] = df["created_at"].dt.to_period("M").astype(str)
        monthly_avg = df.groupby("month")["sentiment_score"].mean().reset_index()
        fig2, ax2 = plt.subplots()
        ax2.plot(monthly_avg["month"], monthly_avg["sentiment_score"], marker="o", color="#2196F3")
        ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
        ax2.set_title("Average Sentiment Over Time")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Score")
        plt.xticks(rotation=45)
        st.pyplot(fig2)

    st.subheader("Most Positive Issues")
    st.dataframe(df.nlargest(5, "sentiment_score")[["title", "sentiment_score", "created_at"]])

    st.subheader("Most Negative Issues")
    st.dataframe(df.nsmallest(5, "sentiment_score")[["title", "sentiment_score", "created_at"]])


# ---------------------------------------------------
# Sidebar - choose mode
# ---------------------------------------------------
st.sidebar.header("Options")
mode = st.sidebar.radio("Choose a mode:", ["Analyze a repo already saved", "Analyze a new repo (live)"])

if mode == "Analyze a repo already saved":
    processed_files = glob.glob(os.path.join("data", "processed", "*_issues_sentiment.csv"))
    repo_names = [os.path.basename(f).replace("_issues_sentiment.csv", "") for f in processed_files]

    if not repo_names:
        st.warning("No saved sentiment files found in data/processed/. "
                   "Run scripts 1-3 first, or switch to 'Analyze a new repo (live)'.")
    else:
        selected_repo = st.sidebar.selectbox("Select a repo:", repo_names)
        df = pd.read_csv(os.path.join("data", "processed", f"{selected_repo}_issues_sentiment.csv"))
        render_dashboard(df, selected_repo)

else:
    repo_input = st.sidebar.text_input("Enter repo (owner/repo):", placeholder="e.g. axios/axios")
    run_button = st.sidebar.button("Analyze")

    if run_button and repo_input:
        if "/" not in repo_input:
            st.error("Please use the format owner/repo, e.g. axios/axios")
        else:
            owner, repo = repo_input.split("/")
            with st.spinner(f"Fetching and analyzing '{repo_input}'..."):
                df = fetch_and_analyze(owner, repo)

            if df.empty:
                st.error("No data found. Check the repo name and try again.")
            else:
                render_dashboard(df, repo_input)