"""On-chain vault data fetching via Multicall3."""

import os
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from eth_abi import decode as abi_decode
from web3 import Web3

NETWORK_CONFIG: dict[str, dict] = {
    "mainnet": {
        "rpc": os.environ.get("ETH_RPC_URL", "https://eth.llamarpc.com"),
        "wallet_rpc": "https://eth.llamarpc.com",
        "explorer": "https://etherscan.io",
        "chain_id": 1,
        "display_name": "Ethereum",
    },
    "katana": {
        "rpc": os.environ.get("KATANA_RPC_URL", "https://rpc.katana.network"),
        "wallet_rpc": "https://rpc.katana.network",
        "explorer": "https://katanascan.com",
        "chain_id": 747474,
        "display_name": "Katana",
    },
    "robinhood": {
        "rpc": os.environ.get("ROBINHOOD_RPC_URL", "https://rpc.mainnet.chain.robinhood.com"),
        "wallet_rpc": "https://rpc.mainnet.chain.robinhood.com",
        "explorer": "https://robinhoodchain.blockscout.com",
        "chain_id": 4663,
        "display_name": "Robinhood",
    },
}


def network_config(network: str) -> dict[str, Any]:
    """Config for a network key. An unknown key (a typo in vaults.json) gets an inert fallback instead of a 500."""
    return NETWORK_CONFIG.get(network) or {"rpc": "", "explorer": "", "chain_id": 0, "display_name": network}


MULTICALL3 = Web3.to_checksum_address("0xcA11bde05977b3631167028862bE2a173976CA11")

VAULT_ABI = [
    {"inputs": [], "name": "asset", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {
        "inputs": [],
        "name": "totalAssets",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "pricePerShare",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {"inputs": [], "name": "decimals", "outputs": [{"type": "uint8"}], "stateMutability": "view", "type": "function"},
]

ERC20_ABI = [
    {"inputs": [], "name": "symbol", "outputs": [{"type": "string"}], "stateMutability": "view", "type": "function"},
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}],
        "name": "allowance",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

MULTICALL3_ABI = [
    {
        "inputs": [
            {"name": "requireSuccess", "type": "bool"},
            {
                "name": "calls",
                "type": "tuple[]",
                "components": [
                    {"name": "target", "type": "address"},
                    {"name": "callData", "type": "bytes"},
                ],
            },
        ],
        "name": "tryAggregate",
        "outputs": [
            {
                "name": "returnData",
                "type": "tuple[]",
                "components": [
                    {"name": "success", "type": "bool"},
                    {"name": "returnData", "type": "bytes"},
                ],
            },
        ],
        "stateMutability": "payable",
        "type": "function",
    }
]

APR_ORACLE = Web3.to_checksum_address("0x1981AD9F44F2EA9aDd2dC4AD7D075c102C70aF92")

APR_ORACLE_ABI = [
    {
        "inputs": [{"name": "_strategy", "type": "address"}, {"name": "_debtChange", "type": "int256"}],
        "name": "getStrategyApr",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "_vault", "type": "address"}],
        "name": "getCurrentApr",
        "outputs": [{"type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

COMPOUNDER_REGISTRY = Web3.to_checksum_address("0xA1b6bAA11A9Ad26060e3F1452f14273dE1f33d17")
KEEPER_MULTICALL = Web3.to_checksum_address("0x075ccC1f86Cb00c9F77f2a9aAF5C9C1Db9cb0d39")
POSITION_MANAGER = Web3.to_checksum_address("0x07F44c47743A2f36414A82b9F558ECFCf0EEdCEf")

REGISTRY_ABI = [
    {
        "inputs": [],
        "name": "config",
        "outputs": [
            {
                "name": "",
                "type": "tuple",
                "components": [
                    {"name": "treasury", "type": "address"},
                    {"name": "feeBps", "type": "uint16"},
                    {"name": "slippageBps", "type": "uint16"},
                    {"name": "twapWindow", "type": "uint32"},
                    {"name": "maxTickDeviation", "type": "uint24"},
                    {"name": "gasPremiumBps", "type": "uint16"},
                    {"name": "gasOverhead", "type": "uint32"},
                    {"name": "maxGasPrice", "type": "uint128"},
                    {"name": "protocolKeeper", "type": "address"},
                    {"name": "paused", "type": "bool"},
                ],
            }
        ],
        "stateMutability": "view",
        "type": "function",
    },
]

COMPOUNDER_SNAPSHOT_COMPONENTS = [
    {"name": "compounder", "type": "address"},
    {"name": "owner", "type": "address"},
    {"name": "version", "type": "uint16"},
    {"name": "keeper", "type": "address"},
    {"name": "active", "type": "bool"},
    {"name": "gasBalance", "type": "uint256"},
    {"name": "minUpToCompound", "type": "uint256"},
    {"name": "lastCompoundAt", "type": "uint40"},
    {"name": "totalUpClaimed", "type": "uint256"},
    {"name": "totalFeesPaid", "type": "uint256"},
    {"name": "totalGasReimbursed", "type": "uint256"},
    {"name": "positionCount", "type": "uint256"},
    {"name": "pendingUp", "type": "uint256"},
]

POSITION_SNAPSHOT_COMPONENTS = [
    {"name": "tokenId", "type": "uint256"},
    {"name": "pool", "type": "address"},
    {"name": "gauge", "type": "address"},
    {"name": "token0", "type": "address"},
    {"name": "token1", "type": "address"},
    {"name": "tickSpacing", "type": "int24"},
    {"name": "tickLower", "type": "int24"},
    {"name": "tickUpper", "type": "int24"},
    {"name": "currentTick", "type": "int24"},
    {"name": "liquidity", "type": "uint128"},
    {"name": "inRange", "type": "bool"},
    {"name": "staked", "type": "bool"},
    {"name": "poolEnabled", "type": "bool"},
    {"name": "earned", "type": "uint256"},
    {"name": "depositedAt", "type": "uint40"},
    {"name": "lastCompoundedAt", "type": "uint40"},
    {"name": "compoundCount", "type": "uint32"},
    {"name": "upClaimed", "type": "uint256"},
]

COMPOUNDER_LENS_ABI = [
    {
        "inputs": [{"name": "user", "type": "address"}],
        "name": "userView",
        "outputs": [
            {"name": "compounder", "type": "address"},
            {"name": "s", "type": "tuple", "components": COMPOUNDER_SNAPSHOT_COMPONENTS},
            {"name": "positions", "type": "tuple[]", "components": POSITION_SNAPSHOT_COMPONENTS},
            {"name": "previous", "type": "address[]"},
        ],
        "stateMutability": "view",
        "type": "function",
    }
]

POSITION_MANAGER_ABI = [
    {
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    }
]

TOKEN_LABELS = {
    "0x0bd7d308f8e1639fab988df18a8011f41eacad73": "WETH",
    "0x5fc5360d0400a0fd4f2af552add042d716f1d168": "USDG",
    "0x57c0e45cb534413d1c20a4240955d6bb250bb4f1": "UP",
}


@dataclass
class VaultInfo:
    ok: bool  # False means the chain could not be read and every other field is a placeholder
    asset_symbol: str
    asset_address: str
    vault_address: str
    explorer_url: str
    total_assets: str
    price_per_share: str
    decimals: int
    asset_balance: str
    vault_balance: str
    asset_balance_raw: str
    vault_balance_raw: str
    allowance_raw: str
    expected_apy: str
    current_apy: str


@dataclass
class CompounderPosition:
    token_id: str
    pool: str
    pool_url: str
    pair: str
    tick_lower: int
    tick_upper: int
    current_tick: int
    liquidity: str
    in_range: bool
    staked: bool
    pool_enabled: bool
    earned_up: str
    earned_up_raw: str
    deposited_at: str
    last_compounded_at: str
    compound_count: int
    up_claimed: str


@dataclass
class CompounderInfo:
    ok: bool
    error: str
    account: str
    has_compounder: bool
    registry_address: str
    registry_url: str
    position_manager_address: str
    protocol_keeper: str
    protocol_paused: bool
    protocol_fee: str
    compounder_address: str
    compounder_url: str
    version: int
    active: bool
    automation_enabled: bool
    gas_balance: str
    gas_balance_raw: str
    min_up_to_compound: str
    min_up_to_compound_raw: str
    last_compound_at: str
    total_up_claimed: str
    total_fees_paid: str
    total_gas_reimbursed: str
    pending_up: str
    pending_up_raw: str
    wallet_position_count: int
    positions: list[CompounderPosition]
    previous_compounders: list[str]


def _get_w3(network: str) -> Web3:
    return Web3(Web3.HTTPProvider(network_config(network)["rpc"]))


def _encode(contract: Any, fn_name: str, args: list | None = None) -> bytes:  # type: ignore[type-arg]
    """Encode a contract function call to bytes."""
    hex_str: str = contract.encode_abi(fn_name, args=args or [])
    return bytes.fromhex(hex_str[2:])


def _multicall(w3: Web3, calls: list[tuple[str, bytes]]) -> list[tuple[bool, bytes]]:
    """Execute calls via Multicall3.tryAggregate."""
    mc = w3.eth.contract(address=MULTICALL3, abi=MULTICALL3_ABI)
    return mc.functions.tryAggregate(False, calls).call()


def _format_amount(raw: int, decimals: int) -> str:
    if decimals == 0:
        return str(raw)
    value = raw / (10**decimals)
    if value == int(value):
        return f"{int(value):,}"
    return f"{value:,.6f}".rstrip("0").rstrip(".")


def _format_apr(apr_raw: int) -> str:
    """Format raw APR (1e18 = 100%) as percentage string."""
    pct = apr_raw / 1e18 * 100
    if pct == 0:
        return "0%"
    return f"{pct:.2f}%"


def _placeholder(address: str, explorer_url: str) -> VaultInfo:
    return VaultInfo(
        ok=False,
        asset_symbol="-",
        asset_address=ZERO_ADDRESS,
        vault_address=address,
        explorer_url=explorer_url,
        total_assets="-",
        price_per_share="-",
        decimals=0,
        asset_balance="-",
        vault_balance="-",
        asset_balance_raw="0",
        vault_balance_raw="0",
        allowance_raw="0",
        expected_apy="-",
        current_apy="-",
    )


def fetch_vault_info(vault: dict[str, str], account: str | None = None) -> VaultInfo:
    """Fetch all vault data (+ optional user balances) via multicall."""
    address = vault["address"]
    network = vault.get("network", "mainnet")
    explorer_url = f"{network_config(network)['explorer']}/address/{address}"

    if address == ZERO_ADDRESS:
        return _placeholder(address, explorer_url)

    try:
        w3 = _get_w3(network)
        vault_addr = Web3.to_checksum_address(address)
        vc = w3.eth.contract(address=vault_addr, abi=VAULT_ABI)

        # Batch 1: vault basic info + APR oracle
        oc = w3.eth.contract(address=APR_ORACLE, abi=APR_ORACLE_ABI)
        results1 = _multicall(
            w3,
            [
                (vault_addr, _encode(vc, "asset")),
                (vault_addr, _encode(vc, "totalAssets")),
                (vault_addr, _encode(vc, "pricePerShare")),
                (vault_addr, _encode(vc, "decimals")),
                (APR_ORACLE, _encode(oc, "getStrategyApr", [vault_addr, 0])),
                (APR_ORACLE, _encode(oc, "getCurrentApr", [vault_addr])),
            ],
        )

        if not all(r[0] for r in results1[:4]):
            return _placeholder(address, explorer_url)

        asset_address = abi_decode(["address"], results1[0][1])[0]
        total_assets_raw = abi_decode(["uint256"], results1[1][1])[0]
        pps_raw = abi_decode(["uint256"], results1[2][1])[0]
        vault_decimals = abi_decode(["uint8"], results1[3][1])[0]

        expected_apy = _format_apr(abi_decode(["uint256"], results1[4][1])[0]) if results1[4][0] else "-"
        current_apy = _format_apr(abi_decode(["uint256"], results1[5][1])[0]) if results1[5][0] else "-"

        # Batch 2: asset symbol + optional user balances
        asset_addr = Web3.to_checksum_address(asset_address)
        tc = w3.eth.contract(address=asset_addr, abi=ERC20_ABI)

        calls2: list[tuple[str, bytes]] = [(asset_addr, _encode(tc, "symbol"))]
        has_account = bool(account and Web3.is_address(account))
        if has_account:
            account_cs = Web3.to_checksum_address(account)  # type: ignore[arg-type]
            calls2.append((asset_addr, _encode(tc, "balanceOf", [account_cs])))
            calls2.append((vault_addr, _encode(tc, "balanceOf", [account_cs])))
            calls2.append((asset_addr, _encode(tc, "allowance", [account_cs, vault_addr])))

        results2 = _multicall(w3, calls2)

        asset_symbol = abi_decode(["string"], results2[0][1])[0] if results2[0][0] else "-"

        asset_balance = "-"
        vault_balance = "-"
        asset_balance_raw = "0"
        vault_balance_raw = "0"
        allowance_raw = "0"
        if has_account and len(results2) >= 4:
            if results2[1][0]:
                ab_raw = abi_decode(["uint256"], results2[1][1])[0]
                asset_balance = _format_amount(ab_raw, vault_decimals)
                asset_balance_raw = str(ab_raw)
            if results2[2][0]:
                vb_raw = abi_decode(["uint256"], results2[2][1])[0]
                vault_balance = _format_amount(vb_raw, vault_decimals)
                vault_balance_raw = str(vb_raw)
            if results2[3][0]:
                allowance_raw = str(abi_decode(["uint256"], results2[3][1])[0])

        return VaultInfo(
            ok=True,
            asset_symbol=asset_symbol,
            asset_address=asset_address,
            vault_address=address,
            explorer_url=explorer_url,
            total_assets=_format_amount(total_assets_raw, vault_decimals),
            price_per_share=_format_amount(pps_raw, vault_decimals),
            decimals=vault_decimals,
            asset_balance=asset_balance,
            vault_balance=vault_balance,
            asset_balance_raw=asset_balance_raw,
            vault_balance_raw=vault_balance_raw,
            allowance_raw=allowance_raw,
            expected_apy=expected_apy,
            current_apy=current_apy,
        )
    except Exception as e:
        print(f"Error fetching vault info for {address}: {e}")
        return _placeholder(address, explorer_url)


def _format_decimal(raw: int, decimals: int, places: int = 4) -> str:
    value = Decimal(raw) / Decimal(10**decimals)
    if value == value.to_integral():
        return f"{value:,.0f}"
    return f"{value:,.{places}f}".rstrip("0").rstrip(".")


def _format_timestamp(timestamp: int) -> str:
    if timestamp == 0:
        return "Never"
    return datetime.fromtimestamp(timestamp, UTC).strftime("%Y-%m-%d %H:%M UTC")


def _token_label(address: str) -> str:
    return TOKEN_LABELS.get(address.lower(), f"{address[:6]}...{address[-4:]}")


def _compounder_placeholder(account: str, error: str = "") -> CompounderInfo:
    explorer = network_config("robinhood")["explorer"]
    return CompounderInfo(
        ok=not error,
        error=error,
        account=account,
        has_compounder=False,
        registry_address=COMPOUNDER_REGISTRY,
        registry_url=f"{explorer}/address/{COMPOUNDER_REGISTRY}",
        position_manager_address=POSITION_MANAGER,
        protocol_keeper=KEEPER_MULTICALL,
        protocol_paused=False,
        protocol_fee="-",
        compounder_address=ZERO_ADDRESS,
        compounder_url="",
        version=0,
        active=False,
        automation_enabled=False,
        gas_balance="0",
        gas_balance_raw="0",
        min_up_to_compound="0",
        min_up_to_compound_raw="0",
        last_compound_at="Never",
        total_up_claimed="0",
        total_fees_paid="0",
        total_gas_reimbursed="0",
        pending_up="0",
        pending_up_raw="0",
        wallet_position_count=0,
        positions=[],
        previous_compounders=[],
    )


def _position_from_snapshot(snapshot: tuple[Any, ...]) -> CompounderPosition:
    explorer = network_config("robinhood")["explorer"]
    pool = snapshot[1]
    return CompounderPosition(
        token_id=str(snapshot[0]),
        pool=pool,
        pool_url=f"{explorer}/address/{pool}",
        pair=f"{_token_label(snapshot[3])} / {_token_label(snapshot[4])}",
        tick_lower=snapshot[6],
        tick_upper=snapshot[7],
        current_tick=snapshot[8],
        liquidity=str(snapshot[9]),
        in_range=snapshot[10],
        staked=snapshot[11],
        pool_enabled=snapshot[12],
        earned_up=_format_decimal(snapshot[13], 18),
        earned_up_raw=str(snapshot[13]),
        deposited_at=_format_timestamp(snapshot[14]),
        last_compounded_at=_format_timestamp(snapshot[15]),
        compound_count=snapshot[16],
        up_claimed=_format_decimal(snapshot[17], 18),
    )


def fetch_compounder_info(account: str | None = None) -> CompounderInfo:
    """Fetch the deployed UP compounder's protocol and optional user state."""
    result = _compounder_placeholder(account or "")
    if not account:
        return result
    if not Web3.is_address(account):
        return _compounder_placeholder(account, "Invalid wallet address")

    try:
        w3 = _get_w3("robinhood")
        account_cs = Web3.to_checksum_address(account)
        registry = w3.eth.contract(address=COMPOUNDER_REGISTRY, abi=REGISTRY_ABI)
        lens = w3.eth.contract(address=KEEPER_MULTICALL, abi=COMPOUNDER_LENS_ABI)
        position_manager = w3.eth.contract(address=POSITION_MANAGER, abi=POSITION_MANAGER_ABI)

        config = registry.functions.config().call()
        compounder, snapshot, positions, previous = lens.functions.userView(account_cs).call()
        wallet_position_count = position_manager.functions.balanceOf(account_cs).call()

        result.protocol_keeper = config[8]
        result.protocol_paused = config[9]
        result.protocol_fee = f"{config[1] / 100:.2f}%"
        result.wallet_position_count = wallet_position_count
        result.previous_compounders = list(previous)
        if compounder.lower() == ZERO_ADDRESS:
            return result

        explorer = network_config("robinhood")["explorer"]
        result.has_compounder = True
        result.compounder_address = compounder
        result.compounder_url = f"{explorer}/address/{compounder}"
        result.version = snapshot[2]
        result.active = snapshot[4]
        result.automation_enabled = snapshot[3].lower() == config[8].lower()
        result.gas_balance = _format_decimal(snapshot[5], 18, 6)
        result.gas_balance_raw = str(snapshot[5])
        result.min_up_to_compound = _format_decimal(snapshot[6], 18)
        result.min_up_to_compound_raw = str(snapshot[6])
        result.last_compound_at = _format_timestamp(snapshot[7])
        result.total_up_claimed = _format_decimal(snapshot[8], 18)
        result.total_fees_paid = _format_decimal(snapshot[9], 18)
        result.total_gas_reimbursed = _format_decimal(snapshot[10], 18, 6)
        result.pending_up = _format_decimal(snapshot[12], 18)
        result.pending_up_raw = str(snapshot[12])
        result.positions = [_position_from_snapshot(position) for position in positions]
        return result
    except Exception as exc:
        print(f"Error fetching compounder info for {account}: {exc}")
        return _compounder_placeholder(account, "Robinhood Chain data is temporarily unavailable")
