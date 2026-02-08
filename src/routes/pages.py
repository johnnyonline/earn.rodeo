"""Page route registration."""

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fasthtml.common import *

from chain import fetch_vault_info
from components import page_shell, vault_detail, vaults_list

VAULTS_PATH = Path(__file__).resolve().parent.parent / "vaults.json"


def _load_vaults() -> list[dict]:
    return json.loads(VAULTS_PATH.read_text())


def register_page_routes(rt: Any) -> None:
    """Register all page routes."""

    @rt("/")
    def home() -> Any:
        vaults = _load_vaults()
        return (
            Title("Cowboy Vaults"),
            page_shell("Cowboy Vaults", vaults_list(vaults)),
        )

    @rt("/vault/{idx}")
    def vault_page(idx: int) -> Any:
        vaults = _load_vaults()
        if idx < 0 or idx >= len(vaults):
            return Response("Vault not found", status_code=404)
        vault = vaults[idx]
        return (
            Title(f"{vault['nickname']} - Cowboy Vaults"),
            page_shell("Cowboy Vaults", vault_detail(vault, idx)),
        )

    @rt("/api/vault/{idx}")
    def vault_api(idx: int, account: str = "") -> Any:
        vaults = _load_vaults()
        if idx < 0 or idx >= len(vaults):
            return Response(json.dumps({"error": "not found"}), status_code=404, media_type="application/json")
        data = fetch_vault_info(vaults[idx], account or None)
        return Response(json.dumps(asdict(data)), media_type="application/json")

    @rt("/favicon.ico")
    def favicon() -> Any:
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🤠</text></svg>'
        return Response(svg, media_type="image/svg+xml")
