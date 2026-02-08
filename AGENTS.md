# ape.tax - Agent Context

## Project Overview
A minimal FastHTML website for ape.tax.

## Tech Stack
- **Framework**: FastHTML
- **Package Manager**: `uv`
- **Styling**: Small custom CSS
- **Deployment**: Vercel

## Development Philosophy
- Minimalistic and simple first
- Reuse existing helpers/components
- Keep functions short and clear
- Less code and less indirection

## Coding Rules
- Use type hints for function parameters and returns
- Keep route registration in `src/routes/pages.py`
- Keep shared UI pieces in `src/components.py`
- Keep global styles in `src/styles.py`
- FastHTML docs are in `./.claude/fasthtml-llms.txt`
