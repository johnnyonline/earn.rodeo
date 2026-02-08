# Cowboy Vaults

Experimental Yearn vaults. Made by cowboys, for cowboys.

## Run with Docker

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

## Deploy to Vercel

Set `ETH_RPC_URL` in the Vercel dashboard environment variables, then deploy.

## Adding vaults

Edit `src/vaults.json`. Each vault entry has:

```json
{
  "emoji1": "🤠",
  "emoji2": "✨",
  "nickname": "Vault Name",
  "short_description": "What this vault does",
  "address": "0x...",
  "network": "mainnet"
}
```