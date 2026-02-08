"""Wallet connection script for Cowboy Vaults."""

from fasthtml.common import Script


def get_wallet_script() -> Script:
    return Script("""
var _web3Modal = null;

function _getWeb3Modal() {
    if (!_web3Modal) {
        _web3Modal = new window.Web3Modal.default({
            cacheProvider: true,
            providerOptions: {},
        });
    }
    return _web3Modal;
}

// --- Network selector ---
window.currentNetwork = localStorage.getItem("selectedNetwork") || "mainnet";

function updateNetworkBtn(network) {
    var btn = document.getElementById("networkBtn");
    if (!btn || !window.NETWORKS) return;
    btn.textContent = window.NETWORKS[network] || network;
}

function toggleNetworkDropdown() {
    var dd = document.getElementById("networkDropdown");
    if (dd) dd.classList.toggle("hidden");
}

function selectNetwork(key) {
    window.currentNetwork = key;
    localStorage.setItem("selectedNetwork", key);
    updateNetworkBtn(key);
    filterVaults(key);
    var dd = document.getElementById("networkDropdown");
    if (dd) dd.classList.add("hidden");
}

function filterVaults(network) {
    var items = document.querySelectorAll(".vault-item");
    items.forEach(function(item) {
        item.style.display = item.getAttribute("data-network") === network ? "" : "none";
    });
}

function truncateAddress(addr) {
    return addr.slice(0, 6) + "..." + addr.slice(-4);
}

function updateWalletBtn(account) {
    var btn = document.getElementById("walletBtn");
    if (!btn) return;
    if (account) {
        btn.textContent = truncateAddress(account);
    } else {
        btn.textContent = "connect wallet";
    }
}

async function fetchVaultData(account) {
    if (typeof window.VAULT_IDX === "undefined") return;
    var url = "/api/vault/" + window.VAULT_IDX;
    if (account) url += "?account=" + encodeURIComponent(account);

    try {
        var resp = await fetch(url);
        if (!resp.ok) return;
        var data = await resp.json();
        window.VAULT_DATA = data;

        var assetEl = document.getElementById("vault-asset");
        var totalEl = document.getElementById("vault-total-assets");
        var ppsEl = document.getElementById("vault-pps");
        var expectedApyEl = document.getElementById("vault-expected-apy");
        var currentApyEl = document.getElementById("vault-current-apy");
        var labelEl = document.getElementById("deposit-balance-label");
        var assetBalEl = document.getElementById("user-asset-balance");
        var vaultBalEl = document.getElementById("user-vault-balance");

        if (assetEl) assetEl.textContent = data.asset_symbol;
        if (totalEl) totalEl.textContent = data.total_assets + " " + data.asset_symbol;
        if (ppsEl) ppsEl.textContent = data.price_per_share;
        if (expectedApyEl) expectedApyEl.textContent = data.expected_apy;
        if (currentApyEl) currentApyEl.textContent = data.current_apy;
        if (labelEl) labelEl.textContent = "Your " + data.asset_symbol + " balance:";
        if (assetBalEl && data.asset_balance !== "-") assetBalEl.textContent = data.asset_balance;
        if (vaultBalEl && data.vault_balance !== "-") vaultBalEl.textContent = data.vault_balance;

        updateDepositState();
        updateWithdrawState();
    } catch (err) {
        console.error("Failed to fetch vault data:", err);
    }
}

function clearBalances() {
    var assetEl = document.getElementById("user-asset-balance");
    var vaultEl = document.getElementById("user-vault-balance");
    if (assetEl) assetEl.textContent = "-";
    if (vaultEl) vaultEl.textContent = "-";
}

// Call this after any tx to refresh all data
window.refetchVaultData = function() {
    fetchVaultData(window.currentAccount || null);
};

function walletToggle() {
    if (window.currentAccount) {
        disconnectWallet();
    } else {
        connectWallet();
    }
}

async function connectWallet() {
    try {
        var modal = _getWeb3Modal();
        var provider = await modal.connect();
        var web3 = new window.Web3(provider);
        var accounts = await web3.eth.getAccounts();
        var account = accounts[0];

        window.currentAccount = account;
        window.currentProvider = provider;
        localStorage.setItem("walletConnected", "true");
        localStorage.setItem("connectedAccount", account);
        updateWalletBtn(account);
        setupProviderListeners(provider);
        fetchVaultData(account);
    } catch (err) {
        console.error("Wallet connection failed:", err);
    }
}

function disconnectWallet() {
    window.currentAccount = null;
    localStorage.removeItem("walletConnected");
    localStorage.removeItem("connectedAccount");
    updateWalletBtn(null);
    clearBalances();

    try {
        if (window.currentProvider && window.currentProvider.close) {
            window.currentProvider.close();
        }
    } catch (e) {
        console.error("Error closing provider:", e);
    }
    window.currentProvider = null;

    try {
        _getWeb3Modal().clearCachedProvider();
    } catch (e) {
        console.error("Error clearing Web3Modal cache:", e);
    }
}

// --- Transaction ABIs ---
var VAULT_TX_ABI = [
    {"inputs": [{"name": "assets", "type": "uint256"}, {"name": "receiver", "type": "address"}], "name": "deposit", "outputs": [{"type": "uint256"}], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "shares", "type": "uint256"}, {"name": "receiver", "type": "address"}, {"name": "owner", "type": "address"}], "name": "redeem", "outputs": [{"type": "uint256"}], "stateMutability": "nonpayable", "type": "function"}
];
var ERC20_TX_ABI = [
    {"inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"type": "bool"}], "stateMutability": "nonpayable", "type": "function"}
];

// --- Decimal <-> raw conversion (no floating point) ---
function rawToDecimal(rawStr, decimals) {
    if (decimals === 0) return rawStr;
    var s = rawStr;
    while (s.length <= decimals) s = "0" + s;
    var intPart = s.slice(0, s.length - decimals);
    var fracPart = s.slice(s.length - decimals).replace(/0+$/, "");
    if (!fracPart) return intPart;
    return intPart + "." + fracPart;
}

function decimalToRaw(val, decimals) {
    if (decimals === 0) return val;
    var parts = val.split(".");
    var intPart = parts[0] || "0";
    var fracPart = (parts[1] || "").slice(0, decimals);
    while (fracPart.length < decimals) fracPart += "0";
    return (BigInt(intPart) * (BigInt(10) ** BigInt(decimals)) + BigInt(fracPart)).toString();
}

// --- Input validation: digits and one decimal point ---
function enforceNumeric(input) {
    var val = input.value.replace(/[^0-9.]/g, "");
    var parts = val.split(".");
    if (parts.length > 2) val = parts[0] + "." + parts.slice(1).join("");
    input.value = val;
}

// --- Button state management ---
function updateDepositState() {
    var input = document.getElementById("deposit-amount");
    var depositBtn = document.getElementById("deposit-btn");
    if (!input || !depositBtn) return;
    if (!window.VAULT_DATA || !window.currentAccount) {
        depositBtn.disabled = true;
        return;
    }
    var val = input.value;
    if (!val || parseFloat(val) === 0) { depositBtn.disabled = true; return; }
    var rawAmount = BigInt(decimalToRaw(val, window.VAULT_DATA.decimals));
    var balance = BigInt(window.VAULT_DATA.asset_balance_raw || "0");
    var allowance = BigInt(window.VAULT_DATA.allowance_raw || "0");
    depositBtn.disabled = !(rawAmount > 0n && rawAmount <= balance && rawAmount <= allowance);
}

function updateWithdrawState() {
    var input = document.getElementById("withdraw-amount");
    var withdrawBtn = document.getElementById("withdraw-btn");
    if (!input || !withdrawBtn) return;
    if (!window.VAULT_DATA || !window.currentAccount) {
        withdrawBtn.disabled = true;
        return;
    }
    var val = input.value;
    if (!val || parseFloat(val) === 0) { withdrawBtn.disabled = true; return; }
    var rawAmount = BigInt(decimalToRaw(val, window.VAULT_DATA.decimals));
    var balance = BigInt(window.VAULT_DATA.vault_balance_raw || "0");
    withdrawBtn.disabled = !(rawAmount > 0n && rawAmount <= balance);
}

// --- Max buttons ---
function handleDepositMax() {
    if (!window.VAULT_DATA) return;
    var input = document.getElementById("deposit-amount");
    if (input) { input.value = rawToDecimal(window.VAULT_DATA.asset_balance_raw || "0", window.VAULT_DATA.decimals); updateDepositState(); }
}

function handleWithdrawMax() {
    if (!window.VAULT_DATA) return;
    var input = document.getElementById("withdraw-amount");
    if (input) { input.value = rawToDecimal(window.VAULT_DATA.vault_balance_raw || "0", window.VAULT_DATA.decimals); updateWithdrawState(); }
}

// --- Cowboy rain ---
function cowboyRain() {
    var count = 30;
    for (var i = 0; i < count; i++) {
        var el = document.createElement("span");
        el.textContent = "🤠";
        el.className = "cowboy-emoji";
        el.style.left = (Math.random() * 100) + "vw";
        el.style.animationDelay = (Math.random() * 1.2) + "s";
        el.style.fontSize = (1.2 + Math.random() * 1.8) + "rem";
        document.body.appendChild(el);
    }
}

// --- Transaction helpers ---
var SPINNER_HTML = '<span class="btn-spinner"></span>';

function btnLoading(btn) {
    btn._origHTML = btn.innerHTML;
    btn.innerHTML = SPINNER_HTML;
    btn.disabled = true;
}

function btnRestore(btn) {
    btn.innerHTML = btn._origHTML;
    btn.disabled = false;
}

// --- Transactions ---
async function handleApprove() {
    if (!window.currentAccount || !window.VAULT_DATA) return;
    var val = document.getElementById("deposit-amount").value;
    if (!val || parseFloat(val) === 0) return;
    var rawAmount = decimalToRaw(val, window.VAULT_DATA.decimals);
    var btn = document.getElementById("approve-btn");
    btnLoading(btn);
    try {
        var web3 = new Web3(window.currentProvider);
        var asset = new web3.eth.Contract(ERC20_TX_ABI, window.VAULT_DATA.asset_address);
        await asset.methods.approve(window.VAULT_DATA.vault_address, rawAmount).send({from: window.currentAccount});
        cowboyRain();
        setTimeout(function() { window.location.reload(); }, 2500);
    } catch (err) {
        console.error("Approve failed:", err);
        btnRestore(btn);
    }
}

async function handleDeposit() {
    if (!window.currentAccount || !window.VAULT_DATA) return;
    var val = document.getElementById("deposit-amount").value;
    if (!val || parseFloat(val) === 0) return;
    var rawAmount = decimalToRaw(val, window.VAULT_DATA.decimals);
    var btn = document.getElementById("deposit-btn");
    btnLoading(btn);
    try {
        var web3 = new Web3(window.currentProvider);
        var vault = new web3.eth.Contract(VAULT_TX_ABI, window.VAULT_DATA.vault_address);
        await vault.methods.deposit(rawAmount, window.currentAccount).send({from: window.currentAccount});
        cowboyRain();
        setTimeout(function() { window.location.reload(); }, 2500);
    } catch (err) {
        console.error("Deposit failed:", err);
        btnRestore(btn);
    }
}

async function handleRedeem() {
    if (!window.currentAccount || !window.VAULT_DATA) return;
    var val = document.getElementById("withdraw-amount").value;
    if (!val || parseFloat(val) === 0) return;
    var rawAmount = decimalToRaw(val, window.VAULT_DATA.decimals);
    var btn = document.getElementById("withdraw-btn");
    btnLoading(btn);
    try {
        var web3 = new Web3(window.currentProvider);
        var vault = new web3.eth.Contract(VAULT_TX_ABI, window.VAULT_DATA.vault_address);
        await vault.methods.redeem(rawAmount, window.currentAccount, window.currentAccount).send({from: window.currentAccount});
        cowboyRain();
        setTimeout(function() { window.location.reload(); }, 2500);
    } catch (err) {
        console.error("Withdraw failed:", err);
        btnRestore(btn);
    }
}

function setupProviderListeners(provider) {
    if (!provider.on) return;

    provider.on("accountsChanged", function(accounts) {
        if (accounts.length === 0) {
            disconnectWallet();
        } else {
            window.currentAccount = accounts[0];
            localStorage.setItem("connectedAccount", accounts[0]);
            updateWalletBtn(accounts[0]);
            fetchVaultData(accounts[0]);
        }
    });

    provider.on("disconnect", function() {
        disconnectWallet();
    });
}

document.addEventListener("DOMContentLoaded", async function() {
    // Network selector init
    updateNetworkBtn(window.currentNetwork);
    filterVaults(window.currentNetwork);

    // Close dropdown on outside click
    document.addEventListener("click", function(e) {
        var sel = document.querySelector(".network-selector");
        if (sel && !sel.contains(e.target)) {
            var dd = document.getElementById("networkDropdown");
            if (dd) dd.classList.add("hidden");
        }
    });

    var btn = document.getElementById("walletBtn");
    if (btn) {
        btn.addEventListener("click", function() {
            walletToggle();
        });
    }

    // Input validation + state updates
    var depositInput = document.getElementById("deposit-amount");
    if (depositInput) depositInput.addEventListener("input", function() { enforceNumeric(depositInput); updateDepositState(); });
    var withdrawInput = document.getElementById("withdraw-amount");
    if (withdrawInput) withdrawInput.addEventListener("input", function() { enforceNumeric(withdrawInput); updateWithdrawState(); });

    var wasConnected = localStorage.getItem("walletConnected");
    if (wasConnected === "true") {
        try {
            var modal = _getWeb3Modal();
            if (modal.cachedProvider) {
                var provider = await modal.connect();
                var web3 = new window.Web3(provider);
                var accounts = await web3.eth.getAccounts();

                if (accounts && accounts.length > 0) {
                    window.currentAccount = accounts[0];
                    window.currentProvider = provider;
                    localStorage.setItem("connectedAccount", accounts[0]);
                    updateWalletBtn(accounts[0]);
                    setupProviderListeners(provider);
                    fetchVaultData(accounts[0]);
                } else {
                    updateWalletBtn(null);
                    fetchVaultData(null);
                }
            } else {
                updateWalletBtn(null);
                fetchVaultData(null);
            }
        } catch (err) {
            console.error("Auto-reconnect failed:", err);
            updateWalletBtn(null);
            fetchVaultData(null);
        }
    } else {
        fetchVaultData(null);
    }
});
""")
