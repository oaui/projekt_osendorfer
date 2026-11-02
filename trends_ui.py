"""Supplied command-line interface and milestone views; students edit trends.py.

The student module is passed in explicitly, so running trends.py never imports
it a second time and the support code has no circular imports.
"""

import argparse
import html
import traceback
from doctest import DocTestFinder, DocTestRunner

from data import load_tweets
from geo import geo_distance, make_position, us_states
from maps import (
    draw_cell,
    draw_dot,
    draw_name,
    draw_state,
    draw_state_outline,
    finish_frame,
    get_canvas,
    message,
)
from view import cell, missing, table, write_view

MIN_TWEETS = 3  # Leave sparsely sampled cells empty.


class ProjectViews:
    """Render results computed by the supplied student module."""

    def __init__(self, project):
        self.project = project
        self.had_errors = False

    def print_sentiment(self, text="Are you virtuous or verminous?"):
        """Print the words in text, annotated by their sentiment scores."""
        words = self.project.extract_words(text.lower())
        assert words, 'No words extracted from "' + text + '"'
        layout = "{0:>" + str(len(max(words, key=len))) + "}: {1:+}"
        for word in words:
            s = self.project.get_word_sentiment(word)
            if self.project.has_sentiment(s):
                print(layout.format(word, self.project.sentiment_value(s)))

    def draw_centered_map(self, center_state="TX", n=10):
        """Draw the n states closest to center_state."""
        us_centers = {n: self.project.find_center(s) for n, s in us_states.items()}
        center = us_centers[center_state.upper()]

        def dist_from_center(name):
            return geo_distance(center, us_centers[name])

        for name in sorted(us_states.keys(), key=dist_from_center)[: int(n)]:
            draw_state(us_states[name])
            draw_name(name, us_centers[name])
        draw_dot(center, 1, 10)  # Mark the center state with a red dot
        finish_frame()

    def draw_state_sentiments(self, state_sentiments):
        """Draw all U.S. states in colors corresponding to their sentiment value.

        Unknown state names are ignored; states without values are colored grey.

        state_sentiments -- A dictionary from state strings to sentiment values
        """
        for name, shapes in us_states.items():
            sentiment = state_sentiments.get(name, None)
            draw_state(shapes, sentiment)
        for name, shapes in us_states.items():
            center = self.project.find_center(shapes)
            draw_name(name, center)

    def draw_map_for_term(self, term="texas"):
        """Draw the sentiment map corresponding to the tweets that contain term.

        Some term suggestions:
        texas, sandwich, obama, my life
        """
        tweets = load_tweets(self.project.make_tweet, term)
        tweets_by_state = self.project.group_tweets_by_state(tweets)
        state_sentiments = self.project.average_sentiments(tweets_by_state)
        self.draw_state_sentiments(state_sentiments)
        for tweet in tweets:
            s = self.project.analyze_tweet_sentiment(tweet)
            if self.project.has_sentiment(s):
                draw_dot(
                    self.project.tweet_location(tweet), self.project.sentiment_value(s)
                )
        finish_frame()

    def draw_map_by_hour(self, term="texas"):
        """Draw the sentiment map for tweets that match term, for each hour."""
        tweets = load_tweets(self.project.make_tweet, term)
        tweets_by_hour = self.project.group_tweets_by_hour(tweets)

        for hour in range(24):
            current_tweets = tweets_by_hour.get(hour, [])
            tweets_by_state = self.project.group_tweets_by_state(current_tweets)
            state_sentiments = self.project.average_sentiments(tweets_by_state)
            self.draw_state_sentiments(state_sentiments)
            message("{0:02}:00-{0:02}:59".format(hour))
            finish_frame(append=True)

    def cell_corners(self, cell_key, size):
        """Return the four corner positions of a grid cell, for drawing it."""
        row, column = cell_key
        south, west = row * size, column * size
        north, east = south + size, west + size
        return [
            make_position(south, west),
            make_position(north, west),
            make_position(north, east),
            make_position(south, east),
        ]

    def draw_heat_map(self, tweets, size=2):
        """Draw the average sentiment of each grid cell under the state borders."""
        tweets_by_cell = self.project.group_tweets_by_cell(tweets, size)
        cell_sentiments = self.project.average_sentiments(tweets_by_cell)
        for cell_key, value in cell_sentiments.items():
            enough = len(tweets_by_cell[cell_key]) >= MIN_TWEETS
            if enough and 25 <= cell_key[0] * size <= 50:  # the 48 connected states
                draw_cell(self.cell_corners(cell_key, size), value)
        for shapes in us_states.values():
            draw_state_outline(shapes)

    def compare_maps(self, term="texas", size=2):
        """Show the state map and the heat map for term as two frames."""
        tweets = load_tweets(self.project.make_tweet, term)
        self.draw_state_sentiments(
            self.project.average_sentiments(self.project.group_tweets_by_state(tweets))
        )
        message(f'"{term}" by state')
        finish_frame(append=True)
        self.draw_heat_map(tweets, size)
        message(f'"{term}" by {size}° cell')
        finish_frame(append=True)

    def render_value(self, function, *args):
        """Render one value, preserving useful feedback for incomplete selectors."""
        try:
            return cell(function(*args))
        except NotImplementedError as error:
            return missing(str(error))
        except Exception as error:
            self.had_errors = True
            return missing(f"{function.__name__}: {type(error).__name__}: {error}")

    def view_words(self, term):
        tweets = load_tweets(self.project.make_tweet, term)[:40]
        rows = [
            [
                html.escape(tweet["text"]),
                self.render_value(self.project.tweet_words, tweet),
                self.render_value(self.project.tweet_time, tweet),
                self.render_value(self.project.tweet_location, tweet),
            ]
            for tweet in tweets
        ]
        write_view(
            f'Milestone 1: tweets containing "{term}"',
            table(["text", "tweet_words", "tweet_time", "tweet_location"], rows),
            note=f"The first {len(rows)} tweets. Red entries explain unfinished work or errors.",
        )

    def word_html(self, word):
        sentiment = self.project.get_word_sentiment(word)
        if not self.project.has_sentiment(sentiment):
            return html.escape(word)
        value = self.project.sentiment_value(sentiment)
        color = "#b2182b" if value > 0 else "#2166ac" if value < 0 else "#444"
        return f'<b style="color:{color}" title="{value:+}">{html.escape(word)}</b>'

    def view_sentiments(self, term):
        tweets = load_tweets(self.project.make_tweet, term)[:40]
        rows = []
        for tweet in tweets:
            try:
                words = self.project.tweet_words(tweet)
                text = " ".join(self.word_html(word) for word in words)
                sentiment = self.project.analyze_tweet_sentiment(tweet)
                average = (
                    f"{self.project.sentiment_value(sentiment):+.3f}"
                    if self.project.has_sentiment(sentiment)
                    else "no known word"
                )
                rows.append([text, average])
            except NotImplementedError as error:
                rows.append([html.escape(tweet["text"]), missing(str(error))])
            except Exception as error:
                self.had_errors = True
                rows.append(
                    [
                        html.escape(tweet["text"]),
                        missing(f"{type(error).__name__}: {error}"),
                    ]
                )
        write_view(
            f'Milestone 2: sentiment of tweets containing "{term}"',
            table(["words (red positive, blue negative)", "average"], rows),
            note="Hover over a coloured word to see its score.",
        )

    def view_centers(self):
        for name, shapes in us_states.items():
            draw_state(shapes)
            center = self.project.find_center(shapes)
            draw_name(name, center)
            draw_dot(center, 1, 4)
        finish_frame()

    def view_state_map(self, term):
        tweets = load_tweets(self.project.make_tweet, term)
        groups = self.project.group_tweets_by_state(tweets)
        averages = self.project.average_sentiments(groups)
        self.draw_state_sentiments(averages)
        if not averages:
            message("No tweets with known sentiment for this selection.")
        finish_frame()

    def show_view(self, number, term="texas"):
        """Keep previews usable during partial implementations and show errors."""
        self.had_errors = False
        canvas = get_canvas()
        canvas.reset()
        canvas.title = f'Milestone {number}: "{term}"'
        try:
            if number == 1:
                self.view_words(term)
            elif number == 2:
                self.view_sentiments(term)
            elif number == 3:
                self.view_centers()
            elif number == 4:
                self.view_state_map(term)
            elif number == 5:
                self.compare_maps(term)
            else:
                raise ValueError("Choose a milestone from 1 to 5.")
        except NotImplementedError as error:
            canvas.clear()
            for shapes in us_states.values():
                draw_state_outline(shapes)
            message(str(error))
            finish_frame(append=number == 5)
        except Exception:
            details = traceback.format_exc()
            write_view(
                canvas.title,
                "<pre>" + html.escape(details) + "</pre>",
                note="Your code raised an error. Read the last line, then find your function above it.",
            )
            return 1
        return int(self.had_errors)


def run_doctests(project, names):
    """Run named functions' doctests, returning a shell exit status."""
    namespace = vars(project)
    finder = DocTestFinder()
    runner = DocTestRunner(verbose=True)
    invalid = False
    for name in names:
        function = namespace.get(name)
        if not callable(function):
            print(f"No function named {name}.")
            invalid = True
            continue
        tests = finder.find(function, name=name, globs=namespace)
        if not any(test.examples for test in tests):
            print(f"No doctest examples found for {name}.")
            invalid = True
            continue
        for test in tests:
            runner.run(test)
    result = runner.summarize()
    if not names:
        print("Specify at least one function after -t.")
        invalid = True
    elif not result.failed and not invalid:
        print(f"All {result.attempted} doctest examples passed.")
    return int(invalid or result.failed > 0)


def run(project, argv=None):
    """Parse commands without importing the student module again."""
    parser = argparse.ArgumentParser(
        description="Explore tweets and test your milestone functions."
    )
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--print_sentiment",
        "-p",
        action="store_true",
        help="print known word scores for the supplied text",
    )
    actions.add_argument(
        "--run_doctests",
        "-t",
        action="store_true",
        help="run doctests for one or more function names",
    )
    actions.add_argument(
        "--draw_centered_map",
        "-d",
        action="store_true",
        help="show the ten states closest to a state code (default: TX)",
    )
    actions.add_argument(
        "--draw_map_for_term",
        "-m",
        action="store_true",
        help="show a state sentiment map with tweet locations",
    )
    actions.add_argument(
        "--draw_map_by_hour",
        "-b",
        action="store_true",
        help="show 24 hourly maps with a slider (Question 14)",
    )
    actions.add_argument(
        "--compare_maps",
        "-c",
        action="store_true",
        help="compare the state and grid maps",
    )
    actions.add_argument(
        "--view",
        "-v",
        type=int,
        choices=range(1, 6),
        metavar="N",
        help="write the preview for milestone 1–5",
    )
    parser.add_argument(
        "text",
        nargs="*",
        metavar="TEXT",
        help="function names, a state code, or a search term (default: texas)",
    )
    args = parser.parse_args(argv)
    text = " ".join(args.text)
    if args.run_doctests:
        return run_doctests(project, text.split())
    views = ProjectViews(project)
    if args.view is not None:
        return views.show_view(args.view, text or "texas")
    get_canvas().reset()
    try:
        if args.print_sentiment:
            views.print_sentiment(text or "Are you virtuous or verminous?")
        elif args.draw_centered_map:
            state = (text or "TX").upper()
            if state not in us_states:
                parser.error(f"Unknown state code: {state}")
            views.draw_centered_map(state)
        elif args.draw_map_for_term:
            views.draw_map_for_term(text or "texas")
        elif args.draw_map_by_hour:
            views.draw_map_by_hour(text or "texas")
        elif args.compare_maps:
            views.compare_maps(text or "texas")
        else:
            parser.print_help()
    except (NotImplementedError, FileNotFoundError) as error:
        print(error)
        return 1
    return 0
