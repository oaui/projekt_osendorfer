# Project 1 — From words to a sentiment map

This is the starter repository for the individual course project. The project
sheet contains the specifications, the paper exercises, and the five
milestones.

## First start

Open this folder in VS Code and install the extension **Live Preview**
(publisher: Microsoft). Then run in the VS Code terminal:

```bash
uv sync
uv run python trends.py --help
uv run python trends.py -t make_tweet
uv run python trends.py -v 1 texas
```

The third command reports failures at the beginning: several functions are
deliberately unfinished. The last command writes `view.html`. Right-click it
in the Explorer and choose **Show Preview**. From then on, the preview reloads
whenever the program writes the file again.

## Looking at your progress

| Command | Shows |
|---|---|
| `uv run python trends.py -v 1 texas` | tweets with their words, time, and position |
| `uv run python trends.py -v 2 texas` | words coloured by sentiment, and each tweet's average |
| `uv run python trends.py -v 3` | every state with its computed centre |
| `uv run python trends.py -v 4 texas` | the sentiment map by state |
| `uv run python trends.py -v 5 texas` | the state map and the grid map |
| `uv run python trends.py -b sandwich` | the map for each hour of the day, with a slider |

Every milestone view works while functions are still missing and names the
next unfinished function. Errors in your code are shown with diagnostic
details; empty results and unknown sentiments are valid results. Instead of
`texas`, you can use `sandwich`, `obama`, or `my life`.

Implement the required functions in `trends.py`, replacing each
`raise NotImplementedError(...)` placeholder. Keep the supplied assertions.
The views and command-line interface are supplied in `trends_ui.py`.
Do not edit the supplied data or support files unless an extension explicitly asks you to do so.

## Checking your work

Use `-t` followed by one or more function names. Failed doctests return a
nonzero exit status, which is expected until those functions work. `--help`
lists all commands. Search commands default to `texas`; terms other than the
four bundled samples require the separately supplied larger dataset.

`view.html` is always written beside these Python files, even when you run
Python from another folder. Open it in a browser and reload manually if you
do not use Live Preview.

The support-code regression checks use the standard library:

```bash
uv run python -m unittest discover -s tests
```

These checks validate the supplied infrastructure, not your exercise answers.
Use the doctests and milestone views to check your own implementations.
