import json as _json
from typing import Any, Sequence

from fasthtml.common import *

from chain import COMPOUNDER_REGISTRY, KEEPER_MULTICALL, NETWORK_CONFIG, POSITION_MANAGER, network_config
from scripts.compounder import get_compounder_script


def vault_item(vault: dict, idx: int) -> Any:
    return Li(
        Span(f"{vault['emoji1']} {vault['emoji2']}", cls="vault-emoji"),
        A(vault["nickname"], href=f"/vault/{idx}", cls="vault-nickname"),
        Span(vault["short_description"], cls="vault-short"),
        cls="vault-item",
        data_network=vault.get("network", "mainnet"),
    )


def compounder_item() -> Any:
    return Li(
        Span("UP", cls="protocol-mark"),
        A("UP Position Compounder", href="/compounder", cls="vault-nickname"),
        Span("Auto-compound up33 concentrated-liquidity positions", cls="vault-short"),
        cls="vault-item",
        data_network="robinhood",
    )


def vaults_list(vaults: Sequence[dict]) -> Any:
    return Ul(compounder_item(), *(vault_item(v, i) for i, v in enumerate(vaults)), cls="vault-list")


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
                            Input(
                                type="text", id="deposit-amount", placeholder="0", inputmode="decimal", cls="ape-input"
                            ),
                            Button("max", id="deposit-max-btn", onclick="handleDepositMax()", cls="max-btn"),
                            cls="input-row",
                        ),
                        Button(
                            "\U0001f680 Approve",
                            id="approve-btn",
                            onclick="handleApprove()",
                            disabled=True,
                            cls="ape-btn-side",
                        ),
                        cls="input-approve-row",
                    ),
                    Button(
                        "\U0001f4b0 Deposit", id="deposit-btn", onclick="handleDeposit()", disabled=True, cls="ape-btn"
                    ),
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


def _stat(label: str, value_id: str) -> Any:
    return Div(Span(label, cls="stat-label"), Strong("-", id=value_id, cls="stat-value"), cls="stat-card")


def compounder_detail() -> Any:
    cfg = network_config("robinhood")
    registry_url = f"{cfg['explorer']}/address/{COMPOUNDER_REGISTRY}"
    config = {
        "registry": COMPOUNDER_REGISTRY,
        "keeper": KEEPER_MULTICALL,
        "positionManager": POSITION_MANAGER,
    }

    return Div(
        Div(
            Span("UP Position Compounder", cls="vault-name"),
            P("Automatically claim UP rewards and add them back to your up33 LP positions.", cls="compounder-lede"),
            Div(
                Span("Network:", cls="kv-label"),
                Span(cfg["display_name"], id="vault-network", onclick="switchToVaultChain()", cls="kv-value"),
                cls="kv-row",
            ),
            Div(
                Span("Registry:", cls="kv-label"),
                A(
                    _truncate_address(COMPOUNDER_REGISTRY),
                    href=registry_url,
                    target="_blank",
                    cls="kv-value vault-link",
                ),
                cls="kv-row",
            ),
            cls="compounder-intro",
        ),
        Div(
            B("Experimental protocol."),
            " Deposited NFTs are held and staked by your personal compounder. Keeper gas reimbursements are experimental; fund only a small working balance.",
            cls="compounder-warning",
        ),
        Div(
            P("Connect a wallet to view or create your compounder.", id="compounder-status", cls="compounder-status"),
            Div(
                P("Your wallet is not connected."),
                Button("Connect wallet", onclick="walletToggle()", cls="primary-btn"),
                id="compounder-connect",
                cls="compounder-panel",
            ),
            Div(
                H2("Create your compounder", cls="compounder-heading"),
                P(
                    "One lightweight contract is created for your wallet. It is the only contract that can hold your deposited position NFTs.",
                    cls="help-text",
                ),
                P(Span("Positions currently in wallet: "), Strong("-", id="wallet-position-count"), cls="help-text"),
                Button(
                    "Create compounder",
                    id="create-compounder-btn",
                    onclick="createCompounder(this)",
                    disabled=True,
                    cls="primary-btn",
                ),
                id="compounder-create",
                cls="compounder-panel hidden",
            ),
            Div(
                Div(
                    Div(
                        H2("Your compounder", cls="compounder-heading"),
                        Div(
                            A("-", id="compounder-address", href="#", target="_blank", cls="vault-link"),
                            Span("-", id="compounder-version", cls="status-pill"),
                            Span("-", id="compounder-active", cls="status-pill"),
                            cls="compounder-title-meta",
                        ),
                    ),
                    Button(
                        "Compound all",
                        id="compound-all-btn",
                        onclick="compoundAllPositions(this)",
                        disabled=True,
                        cls="primary-btn",
                    ),
                    cls="compounder-dashboard-head",
                ),
                Div(
                    _stat("Positions", "compounder-position-count"),
                    _stat("Pending rewards", "compounder-pending"),
                    _stat("Keeper gas", "compounder-gas-balance"),
                    _stat("Minimum per position", "compounder-threshold"),
                    cls="compounder-stats",
                ),
                Div(
                    H3("Add a position", cls="box-heading"),
                    P(
                        "Enter an up33 position-manager NFT ID. Approval and deposit are separate wallet transactions.",
                        cls="help-text",
                    ),
                    Input(
                        type="text",
                        id="position-token-id",
                        placeholder="Position NFT ID",
                        inputmode="numeric",
                        cls="compounder-input",
                    ),
                    Div(
                        Button(
                            "1. Approve NFT",
                            id="approve-position-btn",
                            onclick="approvePosition(this)",
                            disabled=True,
                            cls="secondary-btn",
                        ),
                        Button(
                            "2. Deposit and stake",
                            id="deposit-position-btn",
                            onclick="depositPosition(this)",
                            disabled=True,
                            cls="primary-btn",
                        ),
                        cls="compounder-button-row",
                    ),
                    cls="compounder-panel",
                ),
                Div(
                    H3("Automation", cls="box-heading"),
                    Div(Span("Keeper: "), Strong("-", id="automation-state"), cls="help-text"),
                    Button(
                        "Enable automation",
                        id="automation-btn",
                        onclick="toggleAutomation(this)",
                        disabled=True,
                        cls="secondary-btn",
                    ),
                    Div(
                        Input(
                            type="text",
                            id="fund-gas-amount",
                            placeholder="ETH for keeper gas",
                            inputmode="decimal",
                            cls="compounder-input",
                        ),
                        Button(
                            "Fund gas",
                            id="fund-gas-btn",
                            onclick="fundCompounderGas(this)",
                            disabled=True,
                            cls="secondary-btn",
                        ),
                        cls="compounder-inline-form",
                    ),
                    Div(
                        Input(
                            type="text",
                            id="threshold-amount",
                            placeholder="Minimum UP per position",
                            inputmode="decimal",
                            cls="compounder-input",
                        ),
                        Button(
                            "Set threshold",
                            id="threshold-btn",
                            onclick="setCompounderThreshold(this)",
                            disabled=True,
                            cls="secondary-btn",
                        ),
                        cls="compounder-inline-form",
                    ),
                    Button(
                        "Withdraw all keeper gas",
                        id="withdraw-gas-btn",
                        onclick="withdrawCompounderGas(this)",
                        disabled=True,
                        cls="text-btn",
                    ),
                    cls="compounder-panel",
                ),
                Div(
                    H3("Positions", cls="compounder-heading"),
                    Div(P("No positions deposited.", cls="empty-state"), id="compounder-positions"),
                    cls="compounder-position-section",
                ),
                Details(
                    Summary("Lifetime activity"),
                    _kv("Last compound:", "-", value_id="compounder-last-run"),
                    _kv("UP claimed:", "-", value_id="compounder-total-claimed"),
                    _kv("Protocol fees:", "-", value_id="compounder-total-fees"),
                    _kv("Gas reimbursed:", "-", value_id="compounder-total-reimbursed"),
                    cls="compounder-history",
                ),
                id="compounder-dashboard",
                cls="compounder-dashboard hidden",
            ),
            id="compounder-app",
        ),
        A("< back to vaults", href="/", cls="back-link"),
        Script(f"window.VAULT_NETWORK='robinhood'; window.COMPOUNDER_CONFIG={_json.dumps(config)};"),
        get_compounder_script(),
        cls="vault-detail compounder-detail",
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
