# GitHub Repository Sentiment Analyzer

Analyze the emotional tone of issue discussions in any public GitHub repository — powered by lexicon-based sentiment analysis (VADER) and an interactive Streamlit dashboard.

## What it does

This project fetches issues from any public GitHub repository, cleans the text (removes code blocks, links, and markdown formatting), and runs sentiment analysis to understand the overall mood of the community — whether discussions are trending positive, negative, or neutral over time.

It also includes an interactive dashboard where you can type in any repo name and get a live sentiment breakdown, without touching the code.

## Why I built this

Most sentiment analysis student projects apply the same technique to Twitter or product reviews. I wanted to apply it somewhere less explored — developer communities on GitHub — to see whether a general-purpose sentiment tool like VADER actually holds up on technical, domain-specific text.

**Key finding:** VADER frequently misjudges technical language. For example, in the [thisandagain/sentiment](https://github.com/thisandagain/sentiment) repository, the issue titled *"Install sentiment"* scored -0.975 (strongly negative) despite containing no negative emotion at all — simply because of how the words were interpreted out of context. This highlights a real limitation of lexicon-based sentiment tools when applied outside their intended domain (social media/reviews).

## Features

- Fetches issues from any public GitHub repo via the GitHub REST API
- Cleans text (removes code blocks, URLs, markdown, and bot-generated content)
- Runs sentiment analysis using VADER (lexicon-based approach)
- Visualizes sentiment distribution (Positive/Negative/Neutral) and trends over time
- Interactive Streamlit dashboard for live, no-code analysis of any repo
- Surfaces the most positive and most negative issues for qualitative review

## Tech Stack

- Python
- GitHub REST API
- pandas
- VADER Sentiment (vaderSentiment)
- Matplotlib
- Streamlit

## Project Structure

```
github-sentiment-analyzer/
├── data/
│   ├── raw/                    # Raw data collected from GitHub
│   └── processed/              # Cleaned data + sentiment results
├── scripts/
│   ├── 1_data_collector.py     # Fetches issues from GitHub
│   ├── 2_data_cleaner.py       # Cleans and filters text
│   ├── 3_sentiment_analysis.py # Runs VADER sentiment analysis
│   └── 4_visualize.py          # Generates static charts
├── outputs/
│   └── charts/                 # Saved chart images
├── app.py                      # Interactive Streamlit dashboard
├── requirements.txt
└── README.md
```

## How to Run

1. Clone this repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with your GitHub personal access token:
   ```
   GITHUB_TOKEN=your_token_here
   ```

3. Run the pipeline step by step:
   ```bash
   python scripts/1_data_collector.py
   python scripts/2_data_cleaner.py
   python scripts/3_sentiment_analysis.py
   python scripts/4_visualize.py
   ```

4. Or launch the interactive dashboard:
   ```bash
   streamlit run app.py
   ```

## Limitations

- VADER is a general-purpose sentiment tool and can misinterpret domain-specific technical language (as shown in the key finding above)
- Sentiment analysis is performed at the issue level, not on individual comments
- Results reflect the tone of issue text, not the actual resolution or outcome of the issue

## Future Improvements

- Compare VADER results against a custom sentiment dictionary tuned for developer/technical language
- Extend analysis to issue comments, not just issue bodies
- Add aspect-based sentiment (e.g., separate sentiment for "documentation," "performance," "bugs")