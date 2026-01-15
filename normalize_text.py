#!/usr/bin/env python3
import argparse
import re
import sys
from collections import Counter

# NOTE: Tokenization is done ONLY via this custom regex (NO NLTK tokenizer is used).
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?")

# Small built-in stopword fallback (used if NLTK stopwords corpus isn't available)
BUILTIN_STOPWORDS = {
    "the","a","an","and","or","but","if","then","else","for","to","of","in","on","at","by",
    "is","am","are","was","were","be","been","being","it","this","that","these","those",
    "i","you","he","she","we","they","me","him","her","us","them","my","your","his","their"
}


def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Normalize text and count tokens.")
    p.add_argument("input_path", help="Path to a UTF-8 plain text file")

    # Required flags (names must match assignment)
    p.add_argument("-lowercase", action="store_true", help="Lowercase tokens")
    p.add_argument("-stem", action="store_true", help="Apply stemming")
    p.add_argument("-lemmatize", action="store_true", help="Apply lemmatization")
    p.add_argument("-stopwords", action="store_true", help="Remove stopwords")
    p.add_argument(
        "-myopt",
        action="store_true",
        help="Custom option: remove tokens containing any digit (e.g., 2020, 3rd)"
    )

    # Optional extras (allowed)
    p.add_argument("-min_count", type=int, default=1, help="Only output tokens with count >= min_count")
    p.add_argument("-top", type=int, default=0, help="If >0, only output top N tokens")
    p.add_argument("--plot", action="store_true", help="Also save a rank-frequency bar plot as plot.png")
    p.add_argument("--logx", action="store_true", help="Use log scale on x-axis for plot")
    p.add_argument("--logy", action="store_true", help="Use log scale on y-axis for plot")
    return p


def get_stopwords_set() -> set[str]:
    """
    Try NLTK stopwords; if NLTK/corpus is unavailable, fall back to BUILTIN_STOPWORDS.
    We also warn to stderr so it's obvious when fallback happens (helps reproducibility).
    """
    try:
        from nltk.corpus import stopwords  # type: ignore
        try:
            return set(stopwords.words("english"))
        except LookupError:
            print(
                "Warning: NLTK stopwords corpus not found. Falling back to built-in stopword list.\n"
                "        Fix: python -m nltk.downloader stopwords",
                file=sys.stderr
            )
            return set(BUILTIN_STOPWORDS)
    except Exception:
        print(
            "Warning: NLTK not available for stopwords. Falling back to built-in stopword list.\n"
            "        Fix: pip install nltk",
            file=sys.stderr
        )
        return set(BUILTIN_STOPWORDS)


def build_normalizers(args):
    stemmer = None
    lemmatizer = None

    if args.stem:
        try:
            from nltk.stem import PorterStemmer  # type: ignore
            stemmer = PorterStemmer()
        except Exception:
            print(
                "Error: stemming requested (-stem) but nltk is not available.\n"
                "       Fix: pip install nltk",
                file=sys.stderr
            )
            sys.exit(2)

    if args.lemmatize:
        try:
            from nltk.stem import WordNetLemmatizer  # type: ignore
            lemmatizer = WordNetLemmatizer()

            # PROBE: WordNetLemmatizer often fails at runtime if the WordNet corpus isn't downloaded.
            try:
                _ = lemmatizer.lemmatize("tests")
            except LookupError:
                print(
                    "Error: lemmatization requested (-lemmatize) but WordNet corpus is missing.\n"
                    "       Fix: python -m nltk.downloader wordnet\n"
                    "       (Optional): python -m nltk.downloader omw-1.4",
                    file=sys.stderr
                )
                sys.exit(2)

        except Exception:
            print(
                "Error: lemmatization requested (-lemmatize) but nltk is not available.\n"
                "       Fix: pip install nltk",
                file=sys.stderr
            )
            sys.exit(2)

    stop_set = get_stopwords_set() if args.stopwords else set()

    def normalize_token(tok: str) -> str | None:
        # myopt: drop tokens with any digit
        if args.myopt and any(ch.isdigit() for ch in tok):
            return None

        if args.lowercase:
            tok = tok.lower()

        # Remove stopwords (after lowercase so matching works)
        if args.stopwords and tok in stop_set:
            return None

        # Deterministic order if both enabled: lemmatize -> stem
        if lemmatizer is not None:
            tok = lemmatizer.lemmatize(tok)
        if stemmer is not None:
            tok = stemmer.stem(tok)

        return tok

    return normalize_token


def count_tokens(path: str, normalize_token) -> Counter:
    counts = Counter()
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            for raw in TOKEN_RE.findall(line):
                tok = normalize_token(raw)
                if tok:
                    counts[tok] += 1
    return counts


def write_counts(counts: Counter, min_count: int, top: int):
    items = [(t, c) for t, c in counts.items() if c >= min_count]
    items.sort(key=lambda x: (-x[1], x[0]))  # freq desc, token asc
    if top and top > 0:
        items = items[:top]
    for t, c in items:
        print(f"{t} {c}")


def save_plot(counts: Counter, min_count: int, logx: bool, logy: bool, out_path: str = "plot.png"):
    # Use a non-interactive backend so plotting works in headless environments (CI/servers)
    import matplotlib
    matplotlib.use("Agg")

    import matplotlib.pyplot as plt

    items = [(t, c) for t, c in counts.items() if c >= min_count]
    items.sort(key=lambda x: -x[1])

    freqs = [c for _, c in items]
    ranks = list(range(1, len(freqs) + 1))

    plt.figure()
    plt.bar(ranks, freqs)
    plt.title("Rank–Frequency Plot")
    plt.xlabel("Rank")
    plt.ylabel("Frequency")

    if logx:
        plt.xscale("log")
    if logy:
        plt.yscale("log")

    plt.tight_layout()
    plt.savefig(out_path, dpi=200)


def main():
    args = build_argparser().parse_args()
    normalize_token = build_normalizers(args)
    counts = count_tokens(args.input_path, normalize_token)

    write_counts(counts, min_count=args.min_count, top=args.top)

    total = sum(counts.values())
    print(f"[stats] total_tokens={total} unique_tokens={len(counts)}", file=sys.stderr)

    if args.plot:
        save_plot(counts, min_count=args.min_count, logx=args.logx, logy=args.logy)


if __name__ == "__main__":
    main()
