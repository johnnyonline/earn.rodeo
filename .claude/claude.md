# ape.tax - Claude Context

## Project Overview
ape.tax is a minimal site for experimental Yearn vaults. These are risky, unaudited, test-in-prod vaults that Yearn devs deploy for experimentation. The site exists to give users a simple overview of what's available and to clearly communicate the risk.

### Key principles
- Super simple, minimalistic UI - no bells and whistles
- Vault data lives in a JSON file (`src/vaults.json`) so devs can easily add/remove vaults without touching code
- Always emphasize that these vaults are experimental and unaudited

## Tech Stack
- **Framework**: FastHTML (Python-based web framework)
- **Package Manager**: `uv` (not pip)
- **Styling**: Small custom CSS
- **Deployment**: Vercel

## Development Philosophy
- **Minimalistic**: Keep the UI and code intentionally simple
- **Readable**: Prefer short, clear functions
- **Maintainable**: Centralize reusable layout/components
- **DRY**: Reuse helpers before creating new ones
- **Less Code = Less Debt**

## Code Style & Conventions

### Python
- Use type hints for function parameters and returns
- Keep functions focused and single-purpose
- Avoid unnecessary abstraction
- No emojis in code or commits unless explicitly requested
- Complete FastHTML documentation can be found at `./.claude/fasthtml-llms.txt`

### FastHTML
- Prefer server-rendered HTML
- Keep JS usage minimal and optional
- Use shared components from `src/components.py`
- Use centralized CSS from `src/styles.py`

## Notes for Claude
- Start from existing components/routes and extend, do not duplicate
- Keep UI clean and minimal
- Favor simple, explicit code over cleverness
