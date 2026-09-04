import json as _json
from typing import Any, Sequence

from fasthtml.common import *

from chain import NETWORK_CONFIG, network_config


def vault_item(vault: dict, idx: int) -> Any:
    return Li(
        Span(f"{vault['emoji1']} {vault['emoji2']}", cls="vault-emoji"),
        A(vault["nickname"], href=f"/vault/{idx}", cls="vault-nickname"),
        Span(vault["short_description"], cls="vault-short"),
        cls="vault-item",
        data_network=vault.get("network", "mainnet"),
    )


def vaults_list(vaults: Sequence[dict]) -> Any:
    return Ul(*(vault_item(v, i) for i, v in enumerate(vaults)), cls="vault-list")


def _kv(label: str, value: str, value_id: str = "") -> Any:
    return Div(
        Span(label, cls="kv-label"),
        Span(value, id=value_id, cls="kv-value") if value_id else Span(value, cls="kv-value"),
        cls="kv-row",
    )


def _truncate_address(addr: str) -> str:
    return f"{addr[:6]}...{addr[-4:]}"


def vault_detail(vault: dict, idx: int) -> Any:
    network = vault.get("network", "mainnet")
    cfg = network_config(network)
    explorer_url = f"{cfg['explorer']}/address/{vault['address']}"

    return Div(
        Div(
            Span(f"{vault['emoji1']} {vault['emoji2']} {vault['nickname']}", cls="vault-name"),
            Span(vault["short_description"], cls="vault-desc"),
            Br(),
            _kv("Asset:", "-", value_id="vault-asset"),
            Div(
                Span("Vault:", cls="kv-label"),
                A(
                    _truncate_address(vault["address"]),
                    href=explorer_url,
                    target="_blank",
                    cls="kv-value vault-link",
                ),
                cls="kv-row",
            ),
            Div(
                Span("Network:", cls="kv-label"),
                Span(cfg["display_name"], id="vault-network", onclick="switchToVaultChain()", cls="kv-value"),
                cls="kv-row",
            ),
            Br(),
            _kv("Expected APY:", "-", value_id="vault-expected-apy"),
            _kv("Current APY:", "-", value_id="vault-current-apy"),
            Br(),
            _kv("Total Assets:", "-", value_id="vault-total-assets"),
            _kv("Price Per Share:", "-", value_id="vault-pps"),
            cls="vault-stats",
        ),
        Div(
            Div(
                Div(
                    H3("Deposit", cls="box-heading"),
                    Div(
                        Span("Your balance:", cls="kv-label", id="deposit-balance-label"),
                        Span("-", id="user-asset-balance", cls="kv-value"),
                        cls="kv-row",
                    ),
                    Div(
                        Div(
                            Input(type="text", id="deposit-amount", placeholder="0", inputmode="decimal", cls="ape-input"),
                            Button("max", id="deposit-max-btn", onclick="handleDepositMax()", cls="max-btn"),
                            cls="input-row",
                        ),
                        Button("\U0001f680 Approve", id="approve-btn", onclick="handleApprove()", disabled=True, cls="ape-btn-side"),
                        cls="input-approve-row",
                    ),
                    Button("\U0001f4b0 Deposit", id="deposit-btn", onclick="handleDeposit()", disabled=True, cls="ape-btn"),
                    cls="ape-box",
                ),
                Div(
                    H3("Withdraw", cls="box-heading"),
                    Div(
                        Span("Your vault shares:", cls="kv-label"),
                        Span("-", id="user-vault-balance", cls="kv-value"),
                        cls="kv-row",
                    ),
                    Div(
                        Input(type="text", id="withdraw-amount", placeholder="0", inputmode="decimal", cls="ape-input"),
                        Button("max", id="withdraw-max-btn", onclick="handleWithdrawMax()", cls="max-btn"),
                        cls="input-row",
                    ),
                    Button("💸 Withdraw", id="withdraw-btn", onclick="handleRedeem()", disabled=True, cls="ape-btn"),
                    cls="ape-box",
                ),
                cls="ape-boxes",
            ),
            cls="vault-ape",
        ),
        A("< back to vaults", href="/", cls="back-link"),
        Script(f"window.VAULT_IDX={idx}; window.VAULT_NETWORK={_json.dumps(network)};"),
        cls="vault-detail",
    )


def warning_banner() -> Any:
    return Div(
        B("⚠️ WARNING"),
        " These vaults are experimental and will likely be discarded when the tests are over. "
        "There's a good chance you will lose your funds. ",
        cls="warning-banner",
    )


def footer() -> Any:
    return Div(
        A("Made by cowboys, for cowboys", href="https://x.com/cowboyvaults", target="_blank", cls="footer-link"),
        cls="footer",
    )


def _network_selector() -> Any:
    options = [
        Div(
            cfg["display_name"],
            cls="network-option",
            onclick=f"selectNetwork('{key}')",
        )
        for key, cfg in NETWORK_CONFIG.items()
    ]
    return Div(
        Button("Ethereum", id="networkBtn", onclick="toggleNetworkDropdown()", cls="network-btn"),
        Div(*options, id="networkDropdown", cls="network-dropdown hidden"),
        cls="network-selector",
    )


def page_shell(title: str, left_content: Any) -> Any:
    return Main(
        Div(
            Div(
                Img(src="/static/yfi_logo.png", alt="Yearn logo", cls="logo-img"),
                H1(title, cls="site-title"),
                cls="header-left",
            ),
            Div(
                _network_selector(),
                Button("connect wallet", id="walletBtn", cls="wallet-btn"),
                cls="topbar-right",
            ),
            cls="topbar",
        ),
        Div(
            warning_banner(),
            left_content,
            cls="content-col",
        ),
        footer(),
        cls="page",
    )
