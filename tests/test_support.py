"""Regression checks for supplied infrastructure, without exercise solutions."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import data
import trends
import view
from graphics import Canvas
from trends_ui import ProjectViews, run


class SupportTests(unittest.TestCase):
    def setUp(self):
        # Simulate unfinished work independently of the student's progress.
        self.project = SimpleNamespace(**vars(trends))
        names = (
            "tweet_words tweet_time tweet_location extract_words make_sentiment "
            "has_sentiment sentiment_value analyze_tweet_sentiment find_centroid "
            "find_center find_closest_state group_tweets_by_state average_sentiments "
            "find_cell group_tweets_by_cell most_talkative_state group_tweets_by_hour"
        )
        for name in names.split():

            def unfinished(*args, name=name):
                raise NotImplementedError(f"{name} is not implemented yet")

            setattr(self.project, name, unfinished)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "view.html"
        output_patch = patch.object(view, "VIEW_FILE", self.output)
        output_patch.start()
        self.addCleanup(output_patch.stop)
        quiet = contextlib.redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)

    def test_starter_views_show_unfinished_functions(self):
        for milestone in range(1, 6):
            with self.subTest(milestone=milestone):
                self.assertEqual(run(self.project, ["-v", str(milestone)]), 0)
                self.assertIn("not implemented yet", self.output.read_text())

    def test_partial_grid_implementation_keeps_state_frame(self):
        project = SimpleNamespace(**vars(self.project))
        project.find_center = lambda shapes: (38, -98)
        project.group_tweets_by_state = lambda tweets: {}
        project.average_sentiments = lambda groups: {}
        self.assertEqual(run(project, ["-v", "5"]), 0)
        page = self.output.read_text()
        self.assertIn("group_tweets_by_cell is not implemented yet", page)
        self.assertEqual(page.count('class="frame"'), 2)

    def test_empty_groups_are_valid(self):
        project = SimpleNamespace(**vars(self.project))
        project.find_center = lambda shapes: (38, -98)
        project.group_tweets_by_state = lambda tweets: {}
        project.average_sentiments = lambda groups: {}
        self.assertEqual(run(project, ["-v", "4"]), 0)
        self.assertIn("No tweets with known sentiment", self.output.read_text())
        self.assertNotIn("not implemented yet", self.output.read_text())

    def test_unknown_sentiment_is_valid(self):
        project = SimpleNamespace(**vars(self.project))
        project.tweet_words = lambda tweet: []
        project.analyze_tweet_sentiment = lambda tweet: None
        project.has_sentiment = lambda sentiment: False
        self.assertEqual(run(project, ["-v", "2"]), 0)
        self.assertIn("no known word", self.output.read_text())
        self.assertNotIn("not implemented yet", self.output.read_text())

    def test_actual_errors_are_reported_and_escaped(self):
        project = SimpleNamespace(**vars(self.project))

        def broken(*args):
            raise ValueError("<incorrect>")

        project.find_center = broken
        project.tweet_words = broken
        for milestone in (1, 2, 3, 4, 5):
            project.group_tweets_by_state = broken
            with self.subTest(milestone=milestone):
                self.assertEqual(run(project, ["-v", str(milestone)]), 1)
                page = self.output.read_text()
                self.assertIn("ValueError: &lt;incorrect&gt;", page)
                self.assertNotIn("<incorrect>", page)

    def test_doctest_failures_and_invalid_requests_fail(self):
        for args in (
            ["-t", "make_tweet"],
            ["-t", "absent"],
            ["-t"],
            ["-t", "tweet_words"],
        ):
            with self.subTest(args=args):
                self.assertEqual(run(self.project, args), 1)

    def test_successful_doctest_returns_zero(self):
        self.assertEqual(run(self.project, ["-t", "geo_distance"]), 0)

    def test_cli_rejects_invalid_view_and_conflicting_actions(self):
        for args in (["-v", "6"], ["-v", "1", "-m"], ["-d", "ZZ"]):
            with self.subTest(args=args), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as caught:
                    run(self.project, args)
                self.assertEqual(caught.exception.code, 2)

    def test_data_default_is_bundled(self):
        self.assertTrue(data.load_tweets(trends.make_tweet))

    def test_missing_dataset_does_not_create_cache(self):
        with patch.object(data, "DATA_PATH", Path(self.temp.name)):
            with self.assertRaisesRegex(FileNotFoundError, "larger dataset"):
                data.load_tweets(trends.make_tweet, "unavailable")
            self.assertFalse((Path(self.temp.name) / "unavailable.txt").exists())

    def test_tweet_text_can_contain_tabs_or_be_empty(self):
        fixture = Path(self.temp.name) / "sample.txt"
        fixture.write_text(
            "(38, -122)\tunused\t2011-01-01 12:00:00\tHello\tworld\n"
            "(38, -122)\tunused\t2011-01-01 12:00:00\t\n"
        )
        with patch.object(data, "DATA_PATH", fixture.parent):
            tweets = data.load_tweets(trends.make_tweet, "sample")
        self.assertEqual([tweet["text"] for tweet in tweets], ["hello\tworld", ""])

    def test_frame_sequences_can_be_reset(self):
        canvas = Canvas()
        canvas.set_label("first")
        canvas.finish_frame(append=True)
        canvas.set_label("second")
        canvas.finish_frame(append=True)
        self.assertEqual(self.output.read_text().count('class="frame"'), 2)
        canvas.reset()
        canvas.set_label("new")
        canvas.finish_frame(append=True)
        page = self.output.read_text()
        self.assertNotIn("first", page)
        self.assertNotIn("second", page)
        self.assertIn("frame shown", page)

    def test_valid_empty_and_none_values_are_not_missing(self):
        views = ProjectViews(self.project)
        self.assertEqual(views.render_value(lambda: []), "[]")
        self.assertEqual(views.render_value(lambda: None), "None")


if __name__ == "__main__":
    unittest.main()
