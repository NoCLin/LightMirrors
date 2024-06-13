import logging
import re

from mirrorsrun.proxy.direct import direct_proxy
from mirrorsrun.proxy.file_cache import try_file_based_cache
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

HEADER_AUTH_KEY = "www-authenticate"

service_realm_mapping = {}

# https://github.com/opencontainers/distribution-spec/blob/main/spec.md
name_regex = "[a-z0-9]+((.|_|__|-+)[a-z0-9]+)*(/[a-z0-9]+((.|_|__|-+)[a-z0-9]+)*)*"
reference_regex = "[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}"


def try_extract_image_name(path):
    pattern = r"^/v2/(.*)/([a-zA-Z]+)/(.*)$"
    match = re.search(pattern, path)

    if match:
        assert len(match.groups()) == 3
        name, resource, reference = match.groups()
        assert re.match(name_regex, name)
        assert re.match(reference_regex, reference)
        assert resource in ["manifests", "blobs", "tags"]
        return name, resource, reference

    return None, None, None


def patch_auth_realm(request: Request, response: Response):
    # https://registry-1.docker.io/v2/
    # < www-authenticate: Bearer realm="https://auth.docker.io/token",service="registry.docker.io"

    auth = response.headers.get(HEADER_AUTH_KEY, "")
    if auth.startswith("Bearer "):
        parts = auth.removeprefix("Bearer ").split(",")

        auth_values = {}
        for value in parts:
            key, value = value.split("=")
            value = value.strip('"')
            auth_values[key] = value

        assert "realm" in auth_values
        assert "service" in auth_values
        service_realm_mapping[auth_values["service"]] = auth_values["realm"]

        mirror_url = f"{request.url.scheme}://{request.url.netloc}"
        new_token_url = mirror_url + "/token"
        response.headers[HEADER_AUTH_KEY] = auth.replace(
            auth_values["realm"], new_token_url
        )

    return response


def build_docker_registry_handler(base_url: str, name_mapper=lambda x: x):
    async def handler(request: Request):
        path = request.url.path
        if path == "/token":

            params = request.query_params
            scope = params.get("scope", "")
            service = params.get("service", "")
            parts = scope.split(":")
            assert service
            assert len(parts) == 3
            assert parts[0] == "repository"
            assert parts[1]  # name
            assert parts[2] == "pull"
            parts[1] = name_mapper(parts[1])

            scope = ":".join(parts)

            if not scope or not service:
                return Response(content="Bad Request", status_code=400)

            new_params = {
                "scope": scope,
                "service": service,
            }
            query = "&".join([f"{k}={v}" for k, v in new_params.items()])

            return await direct_proxy(
                request, service_realm_mapping[service] + "?" + query
            )

        if path == "/v2/":
            return await direct_proxy(
                request, base_url + "/v2/", post_process=patch_auth_realm
            )

        if not path.startswith("/v2/"):
            return Response(content="Not Found", status_code=404)

        name, resource, reference = try_extract_image_name(path)

        if not name:
            return Response(content="404 Not Found", status_code=404)

        name = name_mapper(name)

        target_url = base_url + f"/v2/{name}/{resource}/{reference}"

        logger.info(
            f"got docker request, {path=} {name=} {resource=} {reference=} {target_url=}"
        )

        if resource == "blobs":
            return await try_file_based_cache(request, target_url)

        return await direct_proxy(
            request,
            target_url,
        )

    return handler


def dockerhub_name_mapper(name):
    # support docker pull xxx which name without library for dockerhub
    if "/" not in name:
        return f"library/{name}"
    return name


k8s = build_docker_registry_handler(
    "https://registry.k8s.io",
)
quay = build_docker_registry_handler(
    "https://quay.io",
)
ghcr = build_docker_registry_handler(
    "https://ghcr.io",
)
dockerhub = build_docker_registry_handler(
    "https://registry-1.docker.io", name_mapper=dockerhub_name_mapper
)
