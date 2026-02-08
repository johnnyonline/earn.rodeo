# ape.tax

Experimental Yearn vaults. Risky, unaudited, test-in-prod.

## Run with Docker (recommended)

Build and run in one command:

```bash
docker compose up --build
```

Then open `http://localhost:5001`.

Run detached:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

## Adding vaults

Edit `src/vaults.json`. Each vault entry has:

```json
{
  "nickname": "yvUSDC",
  "short_description": "Experimental USDC lending vault",
  "long_description": "Longer description for detail pages.",
  "address": "0x..."
}
```

## Project structure

- `Dockerfile`: container image definition
- `docker-compose.yml`: one-command run setup
- `index.py`: Vercel entrypoint
- `src/main.py`: app wiring
- `src/vaults.json`: vault data (edit this to add/remove vaults)
- `src/routes/pages.py`: route registration
- `src/components.py`: reusable UI components
- `src/styles.py`: centralized CSS
- `.claude/fasthtml-llms.txt`: FastHTML reference docs
