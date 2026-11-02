"""A drawing canvas that writes SVG into view.html instead of opening a window.

You do not need to read or change this file.
"""

import html

from view import write_view


class Canvas:
    """Collect drawing commands as SVG elements, frame by frame.

    Each call of finish_frame ends the current frame and writes view.html.
    A program that draws several frames, such as the map by hour, produces a
    page with a slider and a play button.
    """

    def __init__(self, width=1024, height=768, title="Sentiment map", color="white"):
        self.width = width
        self.height = height
        self.title = title
        self.color = color
        self._elements = []
        self._frames = []
        self._label = ""

    def clear(self):
        """Start the current frame again."""
        self._elements = []

    def draw_polygon(self, points, color="Black", fill_color=None, filled=1, width=1):
        """Draw a polygon given as a list of (x, y) pixel positions."""
        if fill_color is None:
            fill_color = color
        if filled == 0:
            fill_color = "none"
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self._elements.append(
            f'<polygon points="{coords}" fill="{fill_color}" stroke="{color}" '
            f'stroke-width="{width * 0.5}"/>'
        )

    def draw_circle(
        self, center, radius, color="Black", fill_color=None, filled=1, width=1
    ):
        """Draw a circle around center, an (x, y) pixel position."""
        if fill_color is None:
            fill_color = color
        if filled == 0:
            fill_color = "none"
        x, y = center
        self._elements.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{fill_color}" '
            f'stroke="{color}" stroke-width="{width * 0.5}"/>'
        )

    def draw_text(
        self,
        text,
        pos,
        color="Black",
        font="Arial",
        size=12,
        style="normal",
        anchor="nw",
    ):
        """Draw text at pos. anchor "center" centres the text there."""
        x, y = pos
        weight = "bold" if "bold" in style else "normal"
        if anchor == "center":
            align = 'text-anchor="middle" dominant-baseline="middle"'
        else:
            align = 'dominant-baseline="hanging"'
        self._elements.append(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-family="{font}" '
            f'font-size="{size}" font-weight="{weight}" {align}>'
            f"{html.escape(str(text))}</text>"
        )

    def svg(self):
        """Return the current frame as one SVG element."""
        background = (
            f'<rect width="{self.width}" height="{self.height}" fill="{self.color}"/>'
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.width}" '
            f'height="{self.height}" viewBox="0 0 {self.width} {self.height}">'
            + background
            + "".join(self._elements)
            + "</svg>"
        )

    def finish_frame(self, append=False):
        """End the current frame and write all frames so far to view.html.

        With append=True, frames accumulate and are shown with a slider.
        Otherwise this frame replaces any previous sequence.
        """
        if not append:
            self._frames = []
            frames = [(self._label, self.svg())]
        else:
            label = self._label or f"frame {len(self._frames) + 1}"
            self._frames.append((label, self.svg()))
            frames = self._frames
        write_view(
            self.title,
            frames=frames,
            note="Use the slider or Play to step through the frames."
            if len(frames) > 1
            else "",
        )
        self._elements = []
        self._label = ""

    def set_label(self, text):
        """Set the label above the current map."""
        self._label = str(text)

    def reset(self):
        """Start an independent preview without retaining earlier frames."""
        self.clear()
        self._frames = []
        self._label = ""
        self.title = "Sentiment map"
