"""Functions for reading data from the sentiment dictionary and tweet files."""

import re
import string
from ast import literal_eval
from datetime import datetime
from pathlib import Path

# Resolve data relative to this source file, independent of the terminal folder.
DATA_PATH = Path(__file__).resolve().parent / "data"


def load_sentiments(file_name=DATA_PATH / "sentiments.csv"):
    """Read the sentiment file and return a dictionary containing the sentiment
    score of each word, a value from -1 to +1.
    """
    sentiments = {}
    with open(file_name, encoding="utf-8") as source:
        for line in source:
            word, score = line.split(",")
            sentiments[word] = float(score.strip())
    return sentiments


word_sentiments = load_sentiments()


def file_name_for_term(term):
    """Return a valid filename that corresponds to an arbitrary term string."""
    valid_characters = "-_" + string.ascii_letters + string.digits
    no_space = term.replace(" ", "_")
    return "".join(c for c in no_space if c in valid_characters) + ".txt"


def generate_filtered_file(unfiltered_name, term):
    """Return the path to a file containing tweets that match term, generating
    that file if necessary.
    """
    filtered_path = DATA_PATH / file_name_for_term(term)
    if not filtered_path.exists():
        source_path = DATA_PATH / unfiltered_name
        if not source_path.is_file():
            raise FileNotFoundError(
                f'No bundled tweets for "{term}". Choose texas, sandwich, obama, or '
                f'"my life", or supply the larger dataset at {source_path}.'
            )
        print('Generating filtered tweets file for "{0}".'.format(term))
        pattern = re.compile(
            r"(?<!\w)" + re.escape(term) + r"(?!\w)",
            flags=re.IGNORECASE,
        )
        with open(DATA_PATH / unfiltered_name, encoding="utf-8") as source:
            with open(filtered_path, mode="w", encoding="utf-8") as out:
                for line in source:
                    if pattern.search(line):
                        out.write(line)
    return filtered_path


def load_tweets(make_tweet, term="texas", file_name="all_tweets.txt"):
    """Return the list of tweets in file_name that contain term.

    make_tweet -- a constructor that takes four arguments:
      - a string containing the words in the tweet
      - a datetime.datetime object representing the time of the tweet
      - a latitude coordinate
      - a longitude coordinate
    """
    term = term.lower()
    filtered_path = generate_filtered_file(file_name, term)
    tweets = []
    with open(filtered_path, encoding="utf-8") as source:
        for line in source:
            fields = line.rstrip("\r\n").split("\t", 3)
            if len(fields) == 4:
                loc, _, time_text, text = fields
                time = datetime.strptime(time_text, "%Y-%m-%d %H:%M:%S")
                lat, lon = literal_eval(loc)
                tweet = make_tweet(text.lower(), time, lat, lon)
                tweets.append(tweet)
    return tweets
