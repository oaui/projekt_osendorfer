"""Write the project's views as one HTML page, view.html.

Open view.html once in VS Code with the extension "Live Preview" (or in any
browser). Every time the program writes the file again, the preview reloads.
You do not need to read or change this file.
"""

import html
from pathlib import Path

VIEW_FILE = Path(__file__).resolve().with_name("view.html")

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 1.5rem; color: #222; }}
  h1 {{ font-size: 1.4rem; margin: 0 0 .3rem 0; }}
  p.note {{ color: #555; margin: 0 0 1rem 0; }}
  table {{ border-collapse: collapse; font-size: .9rem; }}
  th, td {{ border: 1px solid #ccc; padding: .25rem .5rem; text-align: left;
            vertical-align: top; }}
  th {{ background: #f0f0f0; }}
  .missing {{ color: #b00; font-style: italic; }}
  .frame {{ display: none; }}
  .frame.shown {{ display: block; }}
  .controls {{ margin: .5rem 0; display: flex; gap: .5rem; align-items: center; }}
  .controls label {{ font-weight: bold; min-width: 10rem; }}
  svg {{ background: white; border: 1px solid #ddd; max-width: 100%; height: auto; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="note">{note}</p>
{body}
{script}
</body>
</html>
"""

SCRIPT = """<script>
const frames = document.querySelectorAll('.frame');
const slider = document.getElementById('slider');
const label = document.getElementById('framelabel');
const button = document.getElementById('play');
let timer = null;
function show(i) {
  frames.forEach((f, j) => f.classList.toggle('shown', j === i));
  slider.value = i;
  label.textContent = frames[i].dataset.label;
}
slider.addEventListener('input', () => show(Number(slider.value)));
button.addEventListener('click', () => {
  if (timer) { clearInterval(timer); timer = null; button.textContent = 'Play'; return; }
  button.textContent = 'Pause';
  timer = setInterval(() => show((Number(slider.value) + 1) % frames.length), 700);
});
show(0);
</script>
"""


def missing(text="not implemented yet"):
    """Return HTML for a value that a function did not provide yet."""
    return f'<span class="missing">{html.escape(text)}</span>'


def cell(value):
    """Return escaped HTML for a computed value, including None."""
    return html.escape(str(value))


def table(header, rows):
    """Return an HTML table. rows contains lists of already formatted HTML."""
    head = "".join(f"<th>{html.escape(h)}</th>" for h in header)
    body = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows
    )
    return f"<table><tr>{head}</tr>{body}</table>"


def write_view(title, body="", note="", frames=None):
    """Write view.html with a body of HTML, or with a list of (label, svg)
    frames. Several frames get a slider and a play button."""
    script = ""
    if frames:
        parts = []
        for label, svg in frames:
            parts.append(
                f'<div class="frame" data-label="{html.escape(label)}">{svg}</div>'
            )
        if len(frames) > 1:
            controls = (
                '<div class="controls"><button id="play">Play</button>'
                f'<input id="slider" type="range" min="0" max="{len(frames) - 1}" value="0">'
                '<label id="framelabel"></label></div>'
            )
            script = SCRIPT
        else:
            parts[0] = parts[0].replace('class="frame"', 'class="frame shown"')
            controls = f'<div class="controls"><label>{html.escape(frames[0][0])}</label></div>'
        body = body + controls + "".join(parts)
    page = PAGE.format(
        title=html.escape(title), note=html.escape(note), body=body, script=script
    )
    VIEW_FILE.write_text(page, encoding="utf-8")
    print(f"Wrote {VIEW_FILE.resolve()}")
