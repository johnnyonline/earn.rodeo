# Cowboy Vaults

Experimental Yearn vaults. Made by cowboys, for cowboys.

## Run with Docker

```bash
docker compose up --build
```

Then open `http://localhost:5001`.

The UP Position Compounder is available at `/compounder`. Connect a wallet on
Robinhood Chain to create a personal compounder, deposit up33 position NFTs,
compound or claim rewards, and configure keeper automation.

Run detached:

```bash
docker compose up -d --build
```

Stop:

```bash
docker compose down
```

## Deploy to Vercel

Set `ETH_RPC_URL` and `KATANA_RPC_URL` in the Vercel dashboard environment variables, then deploy. `ROBINHOOD_RPC_URL` is optional and defaults to the public Robinhood Chain endpoint.

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
