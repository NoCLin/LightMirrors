import os

ARIA2_RPC_URL = os.environ.get("ARIA2_RPC_URL", "http://aria2:6800/jsonrpc")
RPC_SECRET = os.environ.get("RPC_SECRET", "")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "local.homeinfra.org")

SCHEME = os.environ.get("SCHEME", None)
assert SCHEME in ["http", "https"]

CACHE_DIR = os.environ.get("CACHE_DIR", "/app/cache/")
EXTERNAL_HOST_ARIA2 = f"aria2.{BASE_DOMAIN}"
EXTERNAL_URL_ARIA2 = f"{SCHEME}://{EXTERNAL_HOST_ARIA2}/aria2/index.html"
