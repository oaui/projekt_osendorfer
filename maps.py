"""Map drawing utilities for U.S. sentiment data."""

from functools import cache

from geo import position_to_xy
from graphics import Canvas

# A fixed gradient of sentiment colors from negative (blue) to positive (red)
# Colors chosen via Cynthia Brewer's Color Brewer (colorbrewer2.com)
SENTIMENT_COLORS = [
    "#313695",
    "#4575B4",
    "#74ADD1",
    "#ABD9E9",
    "#E0F3F8",
    "#FFFFFF",
    "#FEE090",
    "#FDAE61",
    "#F46D43",
    "#D73027",
    "#A50026",
]
GRAY = "#AAAAAA"


def get_sentiment_color(sentiment, sentiment_scale=4):
    """Returns a color corresponding to the sentiment value.

    sentiment -- a number between -1 (negative) and +1 (positive)
    """
    if sentiment is None:
        return GRAY
    scaled = (sentiment_scale * sentiment + 1) / 2
    index = int(scaled * len(SENTIMENT_COLORS))  # Rounds down
    if index < 0:
        index = 0
    if index >= len(SENTIMENT_COLORS):
        index = len(SENTIMENT_COLORS) - 1
    return SENTIMENT_COLORS[index]


def draw_state(shapes, sentiment_value=None):
    """Draw the state polygons in the given color on the canvas.

    shapes -- a list of polygons (each a list of positions)
    sentiment_value -- a number between -1 (negative) and 1 (positive)
    """
    for polygon in shapes:
        vertices = [position_to_xy(position) for position in polygon]
        color = get_sentiment_color(sentiment_value)
        get_canvas().draw_polygon(vertices, fill_color=color)


def draw_state_outline(shapes):
    """Draw only the borders of a state, without filling it.

    shapes -- a list of polygons (which are lists of positions)
    """
    for polygon in shapes:
        vertices = [position_to_xy(position) for position in polygon]
        get_canvas().draw_polygon(vertices, color="#444444", filled=0)


def draw_cell(corners, sentiment_value=None):
    """Fill one grid cell, given by its corner positions, with the color of
    its sentiment value.
    """
    vertices = [position_to_xy(position) for position in corners]
    color = get_sentiment_color(sentiment_value)
    get_canvas().draw_polygon(vertices, color=color, fill_color=color)


def draw_name(name, location):
    """Draw the two-letter postal code at the center of the state.

    location -- a position
    """
    center = position_to_xy(location)
    get_canvas().draw_text(name.upper(), center, anchor="center", style="bold")


def draw_dot(location, sentiment_value=None, radius=3):
    """Draw a small dot at location.

    location -- a position
    sentiment_value -- a number between -1 (negative) and 1 (positive)
    """
    center = position_to_xy(location)
    color = get_sentiment_color(sentiment_value)
    get_canvas().draw_circle(center, radius, fill_color=color)


@cache
def get_canvas():
    """Return the shared canvas used to build the current HTML preview."""
    return Canvas(width=960, height=500)


def finish_frame(append=False):
    """Write the current frame, optionally adding it to a slider sequence."""
    get_canvas().finish_frame(append=append)


def message(s):
    """Display a message."""
    get_canvas().set_label(s)
