import os

ARIA2_RPC_URL = os.environ.get("ARIA2_RPC_URL", "http://aria2:6800/jsonrpc")
RPC_SECRET = os.environ.get("RPC_SECRET", "")
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "local.homeinfra.org")

SCHEME = os.environ.get("SCHEME", "http").lower()
assert SCHEME in ["http", "https"]

CACHE_DIR = os.environ.get("CACHE_DIR", "/app/cache/")
EXTERNAL_HOST_ARIA2 = f"aria2.{BASE_DOMAIN}"
EXTERNAL_URL_ARIA2 = f"{SCHEME}://{EXTERNAL_HOST_ARIA2}/aria2/index.html"

BASE_URL_PYTORCH = os.environ.get("BASE_URL_PYTORCH", "https://download.pytorch.org")
BASE_URL_DOCKERHUB = os.environ.get(
    "BASE_URL_DOCKERHUB", "https://registry-1.docker.io"
)
BASE_URL_NPM = os.environ.get("BASE_URL_NPM", "https://registry.npmjs.org")
BASE_URL_PYPI = os.environ.get("BASE_URL_PYPI", "https://pypi.org")
BASE_URL_PYPI_FILES = os.environ.get(
    "BASE_URL_PYPI_FILES", "https://files.pythonhosted.org"
)

BASE_URL_ALPINE = os.environ.get("BASE_URL_ALPINE", "https://dl-cdn.alpinelinux.org")
BASE_URL_UBUNTU = os.environ.get("BASE_URL_UBUNTU", "http://archive.ubuntu.com")
BASE_URL_UBUNTU_PORTS = os.environ.get(
    "BASE_URL_UBUNTU_PORTS", "http://ports.ubuntu.com"
)

BASE_URL_K8S = os.environ.get("BASE_URL_K8S", "https://registry.k8s.io")
BASE_URL_QUAY = os.environ.get("BASE_URL_QUAY", "https://quay.io")
BASE_URL_GHCR = os.environ.get("BASE_URL_GHCR", "https://ghcr.io")
BASE_URL_NVCR = os.environ.get("BASE_URL_NVCR", "https://nvcr.io")
