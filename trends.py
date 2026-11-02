"""From words to a sentiment map: implement the functions for each milestone.

Replace each NotImplementedError with your code. The supplied interface lives
in trends_ui.py; run this file to use it.
"""

from datetime import datetime
from string import ascii_letters

from data import load_tweets, word_sentiments
from geo import geo_distance, latitude, longitude, make_position, us_states

# Milestones 1 and 2: The Feelings in Tweets


def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as a python dictionary.

    text      -- A string; the text of the tweet, all in lowercase
    time      -- A datetime object; the time that the tweet was posted
    latitude  -- A number; the latitude of the tweet's location
    longitude -- A number; the longitude of the tweet's location

    >>> t = make_tweet("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_words(t)
    ['just', 'ate', 'lunch']
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    >>> longitude(p)
    74
    """ 


    tweet: dict = {
        "text": text, 
        "time": time, 
        "latitude": lat, 
        "longitude": lon
    }

    return tweet


def tweet_words(tweet: dict) -> list:
    """Return a list of the words in the text of a tweet."""
    return extract_words(tweet["text"])


def tweet_time(tweet):
    """Return the datetime that represents when the tweet was posted."""
    return tweet["time"]


def tweet_location(tweet):
    """Return a position (see geo.py) that represents the tweet's location."""
    return make_position(tweet["latitude"], tweet["longitude"])


def tweet_string(tweet):
    """Return a string representing the tweet."""
    return f'"{tweet["text"]}" @ {tweet_location(tweet)}'


def extract_words(text) -> list:
    """Return the words in a tweet, not including punctuation.

    >>> extract_words('')
    []
    >>> extract_words('...123!!!')
    []
    >>> extract_words('Hi...CS-101!end')
    ['Hi', 'CS', 'end']
    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    """
    text = text.replace("#", " ")
    for char in text:
        if char not in ascii_letters:
            text = text.replace(char, " ")

    return text.split()


def make_sentiment(value):
    """Return a sentiment, which represents a value that may not exist.

    >>> s = make_sentiment(0.2)
    >>> t = make_sentiment(None)
    >>> has_sentiment(s)
    True
    >>> has_sentiment(t)
    False
    >>> sentiment_value(s)
    0.2
    >>> has_sentiment(make_sentiment(0.0))
    True
    >>> sentiment_value(make_sentiment(0.0))
    0.0
    """
    assert value is None or -1 <= value <= 1, "Illegal value"
    raise NotImplementedError("make_sentiment is not implemented yet")


def has_sentiment(s):
    """Return whether sentiment s has a value."""
    raise NotImplementedError("has_sentiment is not implemented yet")


def sentiment_value(s):
    """Return the value of a sentiment s."""
    assert has_sentiment(s), "No sentiment value"
    raise NotImplementedError("sentiment_value is not implemented yet")


def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word, or an unknown sentiment if it is absent.

    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    return make_sentiment(word_sentiments.get(word, None))


def analyze_tweet_sentiment(tweet):
    """Return a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.

    If no words in the tweet have a sentiment value, return
    make_sentiment(None).

    >>> has_sentiment(analyze_tweet_sentiment(make_tweet('', None, 0, 0)))
    False
    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """
    raise NotImplementedError("analyze_tweet_sentiment is not implemented yet")


# Milestone 3: The Geometry of Maps


def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p3, p2, p1])
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p2, p1])
    (1, 2, 0)
    """
    raise NotImplementedError("find_centroid is not implemented yet")


def find_center(polygons):
    """Compute the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    raise NotImplementedError("find_center is not implemented yet")


# Milestone 4: The Mood of the Nation


def find_closest_state(tweet, state_centers):
    """Return the name of the state closest to the given tweet's location.

    Use the geo_distance function (already provided) to calculate distance
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a dictionary from state names to positions.

    >>> us_centers = {n: find_center(s) for n, s in us_states.items()}
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
    raise NotImplementedError("find_closest_state is not implemented yet")


def group_tweets_by_state(tweets):
    """Return a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> group_tweets_by_state([])
    {}
    >>> ca_tweets = group_tweets_by_state([sf, ny])['CA']
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    """
    raise NotImplementedError("group_tweets_by_state is not implemented yet")


def average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets

    >>> positive = make_tweet('good', None, 0, 0)
    >>> negative = make_tweet('bad', None, 0, 0)
    >>> unknown = make_tweet('unscoredword', None, 0, 0)
    >>> result = average_sentiments({'AA': [positive, negative], 'BB': [unknown]})
    >>> round(result['AA'], 5)
    0.125
    >>> 'BB' in result
    False
    >>> neutral = make_tweet('love bad', None, 0, 0)
    >>> average_sentiments({'neutral': [neutral], 'empty': []})
    {'neutral': 0.0}
    >>> average_sentiments({})
    {}
    """
    raise NotImplementedError("average_sentiments is not implemented yet")


# Milestone 5: A Finer Grid


def find_cell(position, size):
    """Return the grid cell that contains position, as a tuple (row, column).

    The grid divides the map into squares that are size degrees high and
    wide. The row is the latitude divided by size and rounded down; the column
    is the longitude divided by size and rounded down. Both are integers.

    >>> find_cell(make_position(0, -2), 2)
    (0, -1)
    >>> find_cell(make_position(38.3, -122.1), 1)
    (38, -123)
    >>> find_cell(make_position(38.3, -122.1), 0.5)
    (76, -245)
    >>> find_cell(make_position(40.0, -74.0), 2)
    (20, -37)
    """
    raise NotImplementedError("find_cell is not implemented yet")


def group_tweets_by_cell(tweets, size):
    """Return a dictionary that groups tweets by the grid cell containing them.

    The keys of the returned dictionary are cells (see find_cell), and the
    values are lists of the tweets located in that cell.

    >>> sf = make_tweet("san francisco", None, 37.8, -122.4)
    >>> oakland = make_tweet("oakland", None, 37.8, -122.2)
    >>> ny = make_tweet("new york", None, 40.7, -74.0)
    >>> group_tweets_by_cell([], 1)
    {}
    >>> grouped = group_tweets_by_cell([sf, oakland, ny], 1)
    >>> sorted(grouped)
    [(37, -123), (40, -74)]
    >>> len(grouped[(37, -123)])
    2
    """
    raise NotImplementedError("group_tweets_by_cell is not implemented yet")


# Additions


def most_talkative_state(term):
    """Return the state that has the largest number of tweets containing term.

    Return the alphabetically earliest state code when several states tie.

    >>> most_talkative_state('texas')
    'TX'
    >>> most_talkative_state('sandwich')
    'CA'
    """
    raise NotImplementedError("most_talkative_state is not implemented yet")


def group_tweets_by_hour(tweets):
    """Return a dictionary that groups tweets by the hour they were posted.

    The keys of the returned dictionary are the integers 0 through 23.

    The values are lists of tweets, where tweets_by_hour[i] is the list of all
    tweets that were posted between hour i and hour i + 1. Hour 0 refers to
    midnight, while hour 23 refers to 11:00PM.

    To get started, read the Python Library documentation for datetime objects:
    https://docs.python.org/3/library/datetime.html#datetime.datetime

    tweets -- A list of tweets to be grouped

    >>> morning = make_tweet('morning', datetime(2026, 1, 1, 8, 15), 0, 0)
    >>> evening = make_tweet('evening', datetime(2026, 1, 1, 20, 30), 0, 0)
    >>> grouped = group_tweets_by_hour([morning, evening])
    >>> tweet_words(grouped[8][0])
    ['morning']
    >>> len(grouped[9])
    0
    >>> sorted(group_tweets_by_hour([])) == list(range(24))
    True
    >>> sum(len(tweets) for tweets in group_tweets_by_hour([]).values())
    0
    """
    raise NotImplementedError("group_tweets_by_hour is not implemented yet")


if __name__ == "__main__":
    import sys

    from trends_ui import run

    raise SystemExit(run(sys.modules[__name__]))
