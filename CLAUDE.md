# CLAUDE.md — DataScrub project rules

These rules are durable and apply to all work in this repository, across sessions.

## Project

- **Goal**: DataScrub is a single-page Streamlit app. Upload messy Excel/CSV,
  get a data quality summary, a cleaned dataset, basic stats, a few charts, and
  an Excel report — all downloadable. It should read as a polished internal
  business tool, not a student demo.
- **Stack**: Python, Streamlit, Pandas, OpenPyXL, `plotly.express` (only where
  interactivity is genuinely useful — otherwise use Streamlit native charts).
  Dependencies live in `requirements.txt`, not `pyproject.toml`.
- **Supported inputs**: `.xlsx` and `.csv` only.

## Code organization

- `app.py` is the **UI layer only** — Streamlit widgets, layout, wiring. No
  data logic, no parsing, no cleaning rules inside `app.py`.
- All data loading, profiling, cleaning, chart-data-prep, and report-export
  logic lives in `src/`.
- The app is **single-page**. Do not introduce Streamlit multipage structure
  or additional pages.
- If `app.py` grows past ~300 lines, extract reusable UI helpers into
  `src/ui_components.py`. Do not create this file preemptively.

## Language

- README, all UI text, comments, and docstrings must be written in English.

## Engineering discipline

- Avoid over-engineering: no unnecessary abstractions, no speculative
  extensibility, no features beyond what's asked. Prefer the simplest
  implementation that is still correct and readable.
- Work in stages (see the project plan). Do not jump ahead across stages.
- After every working stage:
  - run or check the app (or run the relevant tests) to confirm it still
    works;
  - summarize only the changed files, concisely;
  - create a meaningful local git commit for that stage.
- When fixing an error: first briefly explain the fix plan, then patch only
  what is necessary. Do not rewrite an entire file for a small fix — use
  targeted edits.

## Testing

- Only test data-processing logic (`src/data_loader.py`, `src/data_profiler.py`,
  `src/cleaner.py`, etc.), using plain in-memory DataFrames with `pytest`.
- Do not write Streamlit UI tests.

## Git

- Commits are local only unless explicitly told otherwise — do not create a
  GitHub remote or push without explicit instruction.
