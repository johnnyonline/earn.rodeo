from fasthtml.common import *


def get_styles():
    return Style("""
@font-face {
    font-family: 'Aeonik';
    src: url('/static/fonts/Aeonik-Light.otf') format('opentype');
    font-weight: 300;
    font-style: normal;
    font-display: swap;
}
@font-face {
    font-family: 'Aeonik';
    src: url('/static/fonts/Aeonik-Regular.otf') format('opentype');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}
@font-face {
    font-family: 'Aeonik';
    src: url('/static/fonts/Aeonik-Bold.otf') format('opentype');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
    height: 100%;
    background: #fff;
    color: #1a1a1a;
    font-family: 'Aeonik', sans-serif;
}

.topbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    padding: 0 28px 24px 48px;
}

.header-left {
    display: flex;
    align-items: center;
    gap: 14px;
}

.topbar-right {
    display: flex;
    align-items: center;
    gap: 4px;
}

.network-selector {
    position: relative;
}

.network-btn {
    font-family: 'Aeonik', sans-serif;
    font-size: 0.9rem;
    padding: 8px 16px;
    border: none;
    background: #fff;
    color: #000;
    cursor: pointer;
    white-space: nowrap;
}

.network-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    background: #fff;
    border: 1px solid #ddd;
    min-width: 140px;
    z-index: 100;
}

.network-dropdown.hidden {
    display: none;
}

.network-option {
    padding: 8px 16px;
    font-family: 'Aeonik', sans-serif;
    font-size: 0.85rem;
    cursor: pointer;
    white-space: nowrap;
}

.network-option:hover {
    background: #000;
    color: #fff;
}

.wallet-btn {
    font-family: 'Aeonik', sans-serif;
    font-size: 0.9rem;
    padding: 8px 16px;
    border: none;
    background: #fff;
    color: #000;
    cursor: pointer;
    white-space: nowrap;
}

.warning-banner {
    background: #ffed4a;
    padding: 8px 28px;
    color: #000;
    font-size: 0.85rem;
    line-height: 1.5;
    font-weight: 400;
    font-family: monospace;
}

.page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: url('/static/background.png') no-repeat fixed right bottom / contain;
}

.content-col {
    max-width: 55vw;
    padding: 0 48px 48px;
    display: flex;
    flex-direction: column;
    gap: 28px;
}

.logo-img {
    width: auto;
    height: 30px;
    position: relative;
    top: -4px;
}

.site-title {
    font-size: 1.92rem;
    font-weight: 700;
    color: #000;
    position: relative;
    top: 2px;
}

.vault-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.vault-item {
    display: flex;
    align-items: baseline;
    gap: 10px;
    padding: 4px 0;
}

.vault-emoji {
    white-space: nowrap;
    font-size: 1rem;
}

.vault-nickname {
    font-weight: 700;
    font-size: 1.15rem;
    color: #000;
    white-space: nowrap;
    text-decoration: none;
}

.vault-nickname:hover {
    text-decoration: underline;
}

.vault-short {
    color: #666;
    font-size: 0.99rem;
    font-weight: 400;
}

.vault-name {
    color: #000;
    font-weight: 700;
    font-size: 1.3rem;
    line-height: 1.6;
}

.vault-desc {
    color: #000;
    font-weight: 700;
    line-height: 1.6;
}

.vault-detail {
    display: flex;
    flex-direction: column;
    gap: 10px;
    font-family: monospace;
    font-size: 0.95rem;
}

.kv-row {
    display: flex;
    gap: 8px;
    line-height: 1.6;
}

.kv-label {
    font-weight: 400;
}

.kv-value {
    font-weight: 400;
}

.vault-link {
    text-decoration: none;
    color: #000;
}

.vault-link:hover {
    text-decoration: underline;
}

.vault-stats, .vault-wallet, .vault-ape {
    display: flex;
    flex-direction: column;
}

.section-heading {
    font-family: monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #000;
    margin-bottom: 12px;
}

.ape-boxes {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 6px;
}

.ape-box {
    --trade-control-h: 38px;
    --max-btn-w: 44px;
    border: 1px dashed #9e9e9e;
    background: #fff;
    padding: 9px 11px 10px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
}

.box-heading {
    font-family: monospace;
    font-size: clamp(0.98rem, 1.2vw, 1.2rem);
    font-weight: 700;
    color: #000;
    line-height: 1;
    margin: 0;
}

.ape-box .kv-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
    line-height: 1.05;
    min-height: 0;
}

.ape-box .kv-label,
.ape-box .kv-value {
    font-family: monospace;
    font-size: clamp(0.76rem, 0.9vw, 0.9rem);
    font-weight: 600;
    color: #2b2b2b;
}

.input-approve-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto;
    grid-auto-rows: var(--trade-control-h);
    gap: 6px;
    margin-top: 0;
    align-items: stretch;
}

.ape-box > .input-row,
.ape-box > .input-approve-row {
    margin-top: 4px;
}

.input-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) var(--max-btn-w);
    border: 0;
    border-radius: 0;
    background: transparent;
    min-width: 0;
    align-items: stretch;
    overflow: visible;
    height: var(--trade-control-h);
}

.input-row:focus-within {
    border-color: transparent;
    box-shadow: none;
}

.input-row:focus-within::after {
    content: none;
}

.ape-input::-webkit-outer-spin-button,
.ape-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}
.ape-input[type=number] {
    -moz-appearance: textfield;
}

input.ape-input {
    font-family: monospace;
    font-size: clamp(0.78rem, 0.95vw, 0.88rem);
    font-weight: 500;
    padding: 0 8px !important;
    border: 1px solid #9a9a9a !important;
    border-right: 1px solid #9a9a9a !important;
    border-radius: 0;
    outline: none !important;
    box-shadow: none !important;
    background: #fff !important;
    color: #222;
    width: 100%;
    min-width: 0;
    height: var(--trade-control-h) !important;
    line-height: calc(var(--trade-control-h) - 2px) !important;
    font-variant-numeric: tabular-nums;
    display: block;
    margin: 0 !important;
    vertical-align: middle;
    transform: none;
    box-sizing: border-box !important;
    -webkit-appearance: none;
    appearance: none;
}

input.ape-input:focus,
input.ape-input:focus-visible {
    outline: none !important;
    box-shadow: none !important;
    border-color: #2563eb !important;
    border-right: 1px solid #2563eb !important;
}

button.max-btn {
    font-family: monospace;
    font-size: clamp(0.72rem, 0.82vw, 0.82rem);
    font-weight: 600;
    padding: 0 8px;
    border: 1px solid #9a9a9a !important;
    border-left: 0 !important;
    border-radius: 0;
    outline: none;
    background: #fff;
    color: #333;
    cursor: pointer;
    width: var(--max-btn-w);
    min-width: var(--max-btn-w);
    max-width: var(--max-btn-w);
    height: var(--trade-control-h) !important;
    min-height: var(--trade-control-h) !important;
    max-height: var(--trade-control-h) !important;
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
}

button.max-btn:hover {
    background: #000;
    color: #fff;
}

button.ape-btn-side {
    font-family: monospace;
    font-size: clamp(0.76rem, 0.9vw, 0.86rem);
    font-weight: 600;
    padding: 0 9px;
    border: 1px solid #9a9a9a;
    border-radius: 0;
    outline: none;
    background: #fff;
    color: #181818;
    cursor: pointer;
    white-space: nowrap;
    height: var(--trade-control-h);
    min-height: var(--trade-control-h);
    max-height: var(--trade-control-h);
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
}

button.ape-btn-side:hover {
    background: #000;
    border-color: #000;
    color: #fff;
}

button.ape-btn {
    font-family: monospace;
    font-size: clamp(0.76rem, 0.88vw, 0.85rem);
    font-weight: 600;
    padding: 0 9px;
    border: 1px solid #b7b7b7;
    border-radius: 0;
    outline: none;
    background: #fff;
    color: #9c9c9c;
    cursor: not-allowed;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 0;
    height: var(--trade-control-h);
    min-height: var(--trade-control-h);
    max-height: var(--trade-control-h);
    line-height: 1;
}

.input-row,
.ape-btn-side,
.ape-btn {
    min-height: var(--trade-control-h);
    max-height: var(--trade-control-h);
}

input.ape-input,
button.max-btn,
button.ape-btn-side,
button.ape-btn {
    margin: 0 !important;
    box-sizing: border-box;
}

button.max-btn,
button.ape-btn-side,
button.ape-btn {
    min-height: var(--trade-control-h) !important;
    height: var(--trade-control-h) !important;
    max-height: var(--trade-control-h) !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    -webkit-appearance: none;
    appearance: none;
}

.ape-btn:not(:disabled) {
    color: #000;
    font-weight: 700;
    border-color: #9a9a9a;
    cursor: pointer;
}

.ape-btn:not(:disabled):hover {
    background: #000;
    border-color: #000;
    color: #fff;
}

.ape-btn:disabled,
.ape-btn[disabled] {
    color: #9a9a9a;
    border-color: #c6c6c6;
    background: #fff;
    cursor: not-allowed;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.btn-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid #ccc;
    border-top-color: #333;
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
}

@keyframes cowboy-fall {
    0% { transform: translateY(-60px) rotate(0deg); opacity: 1; }
    85% { opacity: 1; }
    100% { transform: translateY(105vh) rotate(360deg); opacity: 0; }
}

.cowboy-emoji {
    position: fixed;
    top: -60px;
    font-size: 2rem;
    z-index: 9999;
    pointer-events: none;
    animation: cowboy-fall 2.5s linear forwards;
}

.back-link {
    font-size: 0.9rem;
    color: #666;
    text-decoration: none;
    align-self: flex-start;
    margin-top: 10px;
}

.back-link:hover {
    text-decoration: underline;
}

.footer {
    margin-top: auto;
    padding: 2px 0;
    text-align: center;
}

.footer-link {
    font-family: monospace;
    font-size: 0.65rem;
    color: #666;
    text-decoration: none;
}

.footer-link:hover {
    text-decoration: underline;
}

@media (max-width: 1200px) {
    .ape-boxes {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 860px) {
    .page { background-size: 50%; }
    .content-col { max-width: 100%; padding: 0 20px 24px; }
    .warning-banner { max-width: 100%; }
    .topbar { padding: 0 20px 16px; flex-wrap: wrap; gap: 12px; }
    .ape-box {
        --trade-control-h: 34px;
        padding: 10px;
        gap: 5px;
    }
    .box-heading {
        font-size: 0.94rem;
    }
    .ape-box .kv-label,
    .ape-box .kv-value {
        font-size: 0.74rem;
    }
    .input-approve-row {
        grid-template-columns: 1fr;
        gap: 10px;
    }
    .input-row,
    .ape-btn-side,
    .ape-btn {
        height: var(--trade-control-h);
    }
    .ape-input {
        font-size: 0.76rem;
        padding: 0 8px;
    }
    .max-btn {
        font-size: 0.68rem;
        min-width: 36px;
        padding: 0 7px;
    }
    .ape-btn-side,
    .ape-btn {
        font-size: 0.74rem;
        padding: 0 7px;
    }
}

@media (max-width: 600px) {
    .page { background-image: none; }
}
""")