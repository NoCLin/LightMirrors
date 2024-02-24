import os

ARIA2_RPC_URL = os.environ.get("ARIA2_RPC_URL", 'http://aria2:6800/jsonrpc')
RPC_SECRET = os.environ.get("RPC_SECRET", '')
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", '127.0.0.1.nip.io')

PROXY = os.environ.get("PROXY", None)
CACHE_DIR = os.environ.get("CACHE_DIR", "/app/cache/")

EXTERNAL_HOST_ARIA2 = f"aria2." + BASE_DOMAIN
EXTERNAL_URL_ARIA2 = f"https://" + EXTERNAL_HOST_ARIA2
