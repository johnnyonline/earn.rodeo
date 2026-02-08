"""On-chain vault data fetching via Multicall3."""

import os
from dataclasses import dataclass
from typing import Any

from eth_abi import decode as abi_decode
from web3 import Web3

NETWORK_CONFIG: dict[str, dict] = {
    "mainnet": {
        "rpc": os.environ.get("ETH_RPC_URL", "https://eth.llamarpc.com"),
        "explorer": "https://etherscan.io",
        "chain_id": 1,
        "display_name": "Ethereum",
    },
    "katana": {
        "rpc": os.environ.get("KATANA_RPC_URL", ""),
        "explorer": "https://katanascan.com",
        "chain_id": 747474,
        "display_name": "Katana",
    },
}

MULTICALL3 = Web3.to_checksum_address("0xcA11bde05977b3631167028862bE2a173976CA11")

VAULT_ABI = [
    {"inputs": [], "name": "asset", "outputs": [{"type": "address"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "totalAssets", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "pricePerShare", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "decimals", "outputs": [{"type": "uint8"}], "stateMutability": "view", "type": "function"},
]

ERC20_ABI = [
    {"inputs": [], "name": "symbol", "outputs": [{"type": "string"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "owner", "type": "address"}, {"name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
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
    {"inputs": [{"name": "_strategy", "type": "address"}, {"name": "_debtChange", "type": "int256"}], "name": "getStrategyApr", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"inputs": [{"name": "_vault", "type": "address"}], "name": "getCurrentApr", "outputs": [{"type": "uint256"}], "stateMutability": "view", "type": "function"},
]

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@dataclass
class VaultInfo:
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


def _get_w3(network: str) -> Web3:
    return Web3(Web3.HTTPProvider(NETWORK_CONFIG[network]["rpc"]))


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
        asset_symbol="-", asset_address=ZERO_ADDRESS, vault_address=address,
        explorer_url=explorer_url, total_assets="-", price_per_share="-",
        decimals=0, asset_balance="-", vault_balance="-",
        asset_balance_raw="0", vault_balance_raw="0", allowance_raw="0",
        expected_apy="-", current_apy="-",
    )


def fetch_vault_info(vault: dict[str, str], account: str | None = None) -> VaultInfo:
    """Fetch all vault data (+ optional user balances) via multicall."""
    address = vault["address"]
    network = vault.get("network", "mainnet")
    explorer_url = f"{NETWORK_CONFIG[network]['explorer']}/address/{address}"

    if address == ZERO_ADDRESS:
        return _placeholder(address, explorer_url)

    try:
        w3 = _get_w3(network)
        vault_addr = Web3.to_checksum_address(address)
        vc = w3.eth.contract(address=vault_addr, abi=VAULT_ABI)

        # Batch 1: vault basic info + APR oracle
        oc = w3.eth.contract(address=APR_ORACLE, abi=APR_ORACLE_ABI)
        results1 = _multicall(w3, [
            (vault_addr, _encode(vc, "asset")),
            (vault_addr, _encode(vc, "totalAssets")),
            (vault_addr, _encode(vc, "pricePerShare")),
            (vault_addr, _encode(vc, "decimals")),
            (APR_ORACLE, _encode(oc, "getStrategyApr", [vault_addr, 0])),
            (APR_ORACLE, _encode(oc, "getCurrentApr", [vault_addr])),
        ])

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
