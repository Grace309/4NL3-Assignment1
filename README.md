# Homework 1 — normalize_text

A command-line tool to tokenize a UTF-8 plain text file (custom regex, no NLTK tokenizer), optionally normalize tokens, output sorted token counts, and optionally generate a rank–frequency plot.

## How to Run
Run the script with one required argument (the input text file), plus optional flags. Redirect stdout to save counts:

python normalize_text.py "<path_to_text_file>" [options] > counts.txt

Example (Windows):
py -3.14 normalize_text.py "C:\path\to\book.txt" -lowercase -stopwords --plot --logx --logy > counts.txt

Example (Mac/Linux):
python3 normalize_text.py "/path/to/book.txt" -lowercase -stopwords --plot --logx --logy > counts.txt

Note: The TA can replace <path_to_text_file> with any UTF-8 plain text (.txt) file for testing.

## Dependencies
Basic counting:
- Python 3.14

If you use --plot:
- pip install matplotlib

If you use -stopwords, -stem, or -lemmatize:
- pip install nltk
- python -m nltk.downloader stopwords wordnet
- python -m nltk.downloader omw-1.4

## Output
- Token counts are printed to stdout in the format: token count
  (redirect to counts.txt as shown above)
- If --plot is used, a figure is saved as: plot.png
- Run statistics are printed to stderr (does not affect counts.txt):
  [stats] total_tokens=... unique_tokens=...

## Flags
Assignment-required:
- -lowercase : lowercase tokens
- -stem : stemming (requires NLTK)
- -lemmatize : lemmatization (requires NLTK + wordnet)
- -stopwords : remove stopwords (uses NLTK list if available; otherwise fallback list with warning)
- -myopt : custom option — drop tokens containing any digit (e.g., 2020, 3rd)

Optional:
- -min_count N : only output tokens with count ≥ N (default 1)
- -top N : output only top N tokens (default 0 = all)
- --plot : save rank–frequency plot to plot.png
- --logx, --logy : log scales for plot axes

## Use of Generative AI
I used ChatGPT (OpenAI GPT-5, cloud-based model) to:
- Clarify assignment instructions and deliverables
- Refactor and debug the Python implementation (normalize_text.py)
- Suggest improvements for robustness and plotting
- Help draft this README file

I did not use ChatGPT to generate experimental results or perform analysis — all outputs were produced locally.

## Carbon Footprint Estimate
Following the course policy:
- Model: ChatGPT (GPT-5)
- Hardware type: Cloud GPU/TPU (provider: OpenAI)
- Provider: OpenAI
- Region of compute: Hamilton region
- Time used: ~3 days × 8 hours/day ≈ 24 hours total
- Approximate estimate: ~400 queries × 4.32 g CO₂ ≈ 1.73 kg CO₂
