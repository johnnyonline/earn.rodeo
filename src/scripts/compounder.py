"""Wallet interactions for the UP position compounder."""

from fasthtml.common import Script


def get_compounder_script() -> Script:
    return Script(r"""
window.COMPOUNDER_DATA = null;

var COMPOUNDER_REGISTRY_ABI = [
    {"inputs": [], "name": "createCompounder", "outputs": [{"name": "compounder", "type": "address"}], "stateMutability": "nonpayable", "type": "function"}
];

var POSITION_MANAGER_TX_ABI = [
    {"inputs": [{"name": "to", "type": "address"}, {"name": "tokenId", "type": "uint256"}], "name": "approve", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
];

var COMPOUNDER_TX_ABI = [
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "deposit", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}, {"name": "to", "type": "address"}], "name": "withdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "tokenId", "type": "uint256"}], "name": "claim", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "tokenIds", "type": "uint256[]"}], "name": "compound", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "compoundAll", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "keeper", "type": "address"}], "name": "setKeeper", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [{"name": "amount", "type": "uint256"}], "name": "setMinUpToCompound", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
    {"inputs": [], "name": "fundGas", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"name": "amount", "type": "uint256"}, {"name": "to", "type": "address"}], "name": "withdrawGas", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
];

function compounderWeb3() {
    return new window.Web3(window.currentProvider);
}

function setCompounderStatus(message, isError) {
    var status = document.getElementById("compounder-status");
    if (!status) return;
    status.textContent = message || "";
    status.classList.toggle("status-error", !!isError);
}

function showCompounderSection(id, show) {
    var el = document.getElementById(id);
    if (el) el.classList.toggle("hidden", !show);
}

function setCompounderText(id, value) {
    var el = document.getElementById(id);
    if (el) el.textContent = value;
}

function escapeCompounderHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function compounderCanTransact() {
    return !!(window.currentAccount && window.currentProvider && onRightChain());
}

function compounderContract() {
    var data = window.COMPOUNDER_DATA;
    if (!data || !data.has_compounder) return null;
    return new (compounderWeb3()).eth.Contract(COMPOUNDER_TX_ABI, data.compounder_address);
}

function validIntegerInput(id) {
    var input = document.getElementById(id);
    return !!(input && /^\d+$/.test(input.value) && BigInt(input.value) >= 0n);
}

function validDecimalInput(id) {
    var input = document.getElementById(id);
    return !!(input && /^\d+(\.\d+)?$/.test(input.value) && Number(input.value) >= 0);
}

function positiveDecimalInput(id) {
    return validDecimalInput(id) && BigInt(decimalToRaw(document.getElementById(id).value, 18)) > 0n;
}

window.updateCompounderStates = function() {
    var data = window.COMPOUNDER_DATA;
    var ready = compounderCanTransact();
    var hasCompounder = !!(data && data.ok && data.has_compounder);
    var active = !!(hasCompounder && data.active);
    var hasPositions = !!(hasCompounder && data.positions.length);

    var createBtn = document.getElementById("create-compounder-btn");
    var approveBtn = document.getElementById("approve-position-btn");
    var depositBtn = document.getElementById("deposit-position-btn");
    var compoundAllBtn = document.getElementById("compound-all-btn");
    var automationBtn = document.getElementById("automation-btn");
    var fundBtn = document.getElementById("fund-gas-btn");
    var thresholdBtn = document.getElementById("threshold-btn");
    var withdrawGasBtn = document.getElementById("withdraw-gas-btn");

    if (createBtn) {
        createBtn.disabled = !(ready && data && data.ok && !data.protocol_paused && !hasCompounder);
    }
    if (approveBtn) approveBtn.disabled = !(ready && active && validIntegerInput("position-token-id"));
    if (depositBtn) depositBtn.disabled = !(ready && active && validIntegerInput("position-token-id"));
    if (compoundAllBtn) compoundAllBtn.disabled = !(ready && active && hasPositions);
    if (automationBtn) automationBtn.disabled = !(ready && active);
    if (fundBtn) fundBtn.disabled = !(ready && active && positiveDecimalInput("fund-gas-amount"));
    if (thresholdBtn) thresholdBtn.disabled = !(ready && active && validDecimalInput("threshold-amount"));
    if (withdrawGasBtn) withdrawGasBtn.disabled = !(ready && hasCompounder && BigInt(data.gas_balance_raw || "0") > 0n);

    document.querySelectorAll(".position-action").forEach(function(button) {
        button.disabled = !(ready && hasCompounder);
    });
    document.querySelectorAll(".compound-position-action").forEach(function(button) {
        button.disabled = !(ready && active && button.dataset.poolEnabled === "true");
    });
    document.querySelectorAll(".claim-position-action").forEach(function(button) {
        button.disabled = !(ready && hasCompounder && button.dataset.staked === "true");
    });

    if (window.currentAccount && !onRightChain()) {
        setCompounderStatus("Wallet is on the wrong network. Switch to Robinhood Chain to transact.", true);
    }
};

function positionCard(position) {
    var range = position.in_range ? "in range" : "out of range";
    var custody = position.staked ? "staked" : "unstaked";
    var enabled = position.pool_enabled ? "pool active" : "pool disabled";
    var id = escapeCompounderHtml(position.token_id);
    return '<article class="position-card">' +
        '<div class="position-title-row"><strong>' + escapeCompounderHtml(position.pair) + '</strong>' +
        '<a href="' + escapeCompounderHtml(position.pool_url) + '" target="_blank" rel="noreferrer">pool</a></div>' +
        '<div class="position-meta">Position #' + id + ' · ' + range + ' · ' + custody + ' · ' + enabled + '</div>' +
        '<dl class="position-grid">' +
        '<div><dt>Pending</dt><dd>' + escapeCompounderHtml(position.earned_up) + ' UP</dd></div>' +
        '<div><dt>Compounds</dt><dd>' + escapeCompounderHtml(position.compound_count) + '</dd></div>' +
        '<div><dt>Current tick</dt><dd>' + escapeCompounderHtml(position.current_tick) + '</dd></div>' +
        '<div><dt>Range</dt><dd>' + escapeCompounderHtml(position.tick_lower) + ' to ' + escapeCompounderHtml(position.tick_upper) + '</dd></div>' +
        '</dl>' +
        '<div class="position-actions">' +
        '<button class="compact-btn position-action compound-position-action" data-pool-enabled="' + position.pool_enabled + '" onclick="compoundPosition(\'' + id + '\', this)">Compound</button>' +
        '<button class="compact-btn position-action claim-position-action" data-staked="' + position.staked + '" onclick="claimPosition(\'' + id + '\', this)">Claim UP</button>' +
        '<button class="compact-btn danger-btn position-action" onclick="withdrawPosition(\'' + id + '\', this)">Withdraw NFT</button>' +
        '</div></article>';
}

function renderCompounderData(data) {
    var connected = !!window.currentAccount;
    showCompounderSection("compounder-connect", !connected);
    showCompounderSection("compounder-create", connected && data.ok && !data.has_compounder);
    showCompounderSection("compounder-dashboard", connected && data.ok && data.has_compounder);

    if (!data.ok) {
        setCompounderStatus(data.error || "Protocol data is unavailable.", true);
        return;
    }
    if (!connected) {
        setCompounderStatus("Connect a wallet to view or create your compounder.", false);
        return;
    }
    if (!data.has_compounder) {
        setCompounderText("wallet-position-count", data.wallet_position_count);
        setCompounderStatus(
            data.protocol_paused ? "Protocol is currently paused." : "No compounder exists for this wallet yet.",
            data.protocol_paused
        );
        window.updateCompounderStates();
        return;
    }

    var link = document.getElementById("compounder-address");
    if (link) {
        link.textContent = truncateAddress(data.compounder_address);
        link.href = data.compounder_url;
    }
    setCompounderText("compounder-version", "v" + data.version);
    setCompounderText("compounder-active", data.active ? "Active" : "Inactive");
    setCompounderText("compounder-position-count", data.positions.length);
    setCompounderText("compounder-pending", data.pending_up + " UP");
    setCompounderText("compounder-gas-balance", data.gas_balance + " ETH");
    setCompounderText("compounder-threshold", data.min_up_to_compound + " UP");
    setCompounderText("compounder-last-run", data.last_compound_at);
    setCompounderText("compounder-total-claimed", data.total_up_claimed + " UP");
    setCompounderText("compounder-total-fees", data.total_fees_paid + " UP");
    setCompounderText("compounder-total-reimbursed", data.total_gas_reimbursed + " ETH");
    setCompounderText("automation-state", data.automation_enabled ? "Enabled" : "Disabled");

    var automationBtn = document.getElementById("automation-btn");
    if (automationBtn) automationBtn.textContent = data.automation_enabled ? "Disable automation" : "Enable automation";

    var positions = document.getElementById("compounder-positions");
    if (positions) {
        positions.innerHTML = data.positions.length
            ? data.positions.map(positionCard).join("")
            : '<p class="empty-state">No positions deposited.</p>';
    }

    setCompounderStatus(data.protocol_paused ? "Protocol is currently paused." : "Protocol data is current.", data.protocol_paused);
    window.updateCompounderStates();
}

window.fetchCompounderData = async function(account) {
    if (!document.getElementById("compounder-app")) return;
    if (!account) {
        window.COMPOUNDER_DATA = null;
        renderCompounderData({ok: true, has_compounder: false});
        return;
    }

    setCompounderStatus("Loading on-chain data...", false);
    try {
        var response = await fetch("/api/compounder?account=" + encodeURIComponent(account));
        var data = await response.json();
        window.COMPOUNDER_DATA = data;
        renderCompounderData(data);
    } catch (error) {
        console.error("Failed to fetch compounder data:", error);
        window.COMPOUNDER_DATA = null;
        renderCompounderData({ok: false, error: "Could not load Robinhood Chain data."});
    }
};

async function runCompounderTransaction(button, pendingMessage, send) {
    if (!compounderCanTransact()) return;
    btnLoading(button);
    setCompounderStatus(pendingMessage, false);
    try {
        var receipt = await send();
        setCompounderStatus("Transaction confirmed: " + truncateAddress(receipt.transactionHash), false);
        cowboyRain();
        await window.fetchCompounderData(window.currentAccount);
    } catch (error) {
        console.error(pendingMessage, error);
        setCompounderStatus(error.message || "Transaction was not completed.", true);
    } finally {
        btnRestore(button);
    }
}

async function createCompounder(button) {
    await runCompounderTransaction(button, "Creating your compounder...", async function() {
        var registry = new (compounderWeb3()).eth.Contract(COMPOUNDER_REGISTRY_ABI, window.COMPOUNDER_CONFIG.registry);
        return registry.methods.createCompounder().send({from: window.currentAccount});
    });
}

async function approvePosition(button) {
    var tokenId = document.getElementById("position-token-id").value;
    await runCompounderTransaction(button, "Approving the position NFT...", async function() {
        var manager = new (compounderWeb3()).eth.Contract(POSITION_MANAGER_TX_ABI, window.COMPOUNDER_CONFIG.positionManager);
        return manager.methods.approve(window.COMPOUNDER_DATA.compounder_address, tokenId).send({from: window.currentAccount});
    });
}

async function depositPosition(button) {
    var tokenId = document.getElementById("position-token-id").value;
    await runCompounderTransaction(button, "Depositing and staking the position...", async function() {
        return compounderContract().methods.deposit(tokenId).send({from: window.currentAccount});
    });
}

async function compoundAllPositions(button) {
    await runCompounderTransaction(button, "Compounding all eligible positions...", async function() {
        return compounderContract().methods.compoundAll().send({from: window.currentAccount});
    });
}

async function compoundPosition(tokenId, button) {
    await runCompounderTransaction(button, "Compounding position #" + tokenId + "...", async function() {
        return compounderContract().methods.compound([tokenId]).send({from: window.currentAccount});
    });
}

async function claimPosition(tokenId, button) {
    await runCompounderTransaction(button, "Claiming UP from position #" + tokenId + "...", async function() {
        return compounderContract().methods.claim(tokenId).send({from: window.currentAccount});
    });
}

async function withdrawPosition(tokenId, button) {
    if (!window.confirm("Withdraw position #" + tokenId + " to your wallet? Pending UP will also be claimed.")) return;
    await runCompounderTransaction(button, "Withdrawing position #" + tokenId + "...", async function() {
        return compounderContract().methods.withdraw(tokenId, window.currentAccount).send({from: window.currentAccount});
    });
}

async function toggleAutomation(button) {
    var keeper = window.COMPOUNDER_DATA.automation_enabled
        ? "0x0000000000000000000000000000000000000000"
        : window.COMPOUNDER_DATA.protocol_keeper;
    await runCompounderTransaction(button, "Updating keeper automation...", async function() {
        return compounderContract().methods.setKeeper(keeper).send({from: window.currentAccount});
    });
}

async function fundCompounderGas(button) {
    var amount = document.getElementById("fund-gas-amount").value;
    var value = decimalToRaw(amount, 18);
    await runCompounderTransaction(button, "Funding keeper gas...", async function() {
        return compounderContract().methods.fundGas().send({from: window.currentAccount, value: value});
    });
}

async function setCompounderThreshold(button) {
    var amount = document.getElementById("threshold-amount").value;
    var raw = decimalToRaw(amount, 18);
    await runCompounderTransaction(button, "Updating the UP threshold...", async function() {
        return compounderContract().methods.setMinUpToCompound(raw).send({from: window.currentAccount});
    });
}

async function withdrawCompounderGas(button) {
    await runCompounderTransaction(button, "Withdrawing the keeper gas balance...", async function() {
        return compounderContract().methods.withdrawGas(
            window.COMPOUNDER_DATA.gas_balance_raw,
            window.currentAccount
        ).send({from: window.currentAccount});
    });
}

document.addEventListener("DOMContentLoaded", function() {
    if (!document.getElementById("compounder-app")) return;
    window.currentNetwork = "robinhood";
    localStorage.setItem("selectedNetwork", "robinhood");
    updateNetworkBtn("robinhood");

    ["position-token-id", "fund-gas-amount", "threshold-amount"].forEach(function(id) {
        var input = document.getElementById(id);
        if (input) input.addEventListener("input", window.updateCompounderStates);
    });
    window.updateCompounderStates();
});
""")
