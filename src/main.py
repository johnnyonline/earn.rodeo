"""Main FastHTML application entry point."""

from fasthtml.common import *

from routes.pages import register_page_routes
from scripts.wallet import get_wallet_script
from styles import get_styles

app, rt = fast_app(hdrs=[
    get_styles(),
    Script(src="https://unpkg.com/web3modal@1.9.12/dist/index.js"),
    Script(src="https://unpkg.com/web3@1.10.0/dist/web3.min.js"),
    get_wallet_script(),
])
register_page_routes(rt)

if __name__ == "__main__":
    serve()
