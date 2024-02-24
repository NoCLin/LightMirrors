<div align="center">

# LightMirrors

LightMirrors是一个开源的缓存镜像站服务，用于加速软件包下载和镜像拉取。
目前支持**DockerHub**、PyPI、PyTorch、NPM等镜像缓存服务。

<a href='https://github.com/NoCLin/LightMirrors/'><img src='https://img.shields.io/badge/Light-Mirrors-green'></a>
<a href='https://github.com/homeinfra-org/infra'><img src='https://img.shields.io/static/v1?label=Home&message=Infra&color=orange'></a>
[![GitHub](https://img.shields.io/github/stars/NoCLin/LightMirrors?style=social)](https://github.com/NoCLin/LightMirrors)
[![GitHub](https://img.shields.io/github/forks/NoCLin/LightMirrors?style=social)](https://github.com/NoCLin/LightMirrors)

![Demo](docs/images/1.png)

</div>


---

## Quick Start

### Prerequisites

- docker + docker-compose.
- 一个域名，设置 `*.yourdomain` 的A记录指向您服务器的IP.
    - `*.local.homeinfra.org` 默认指向 `127.0.0.1`，本地测试可以直接使用。
- 代理服务器（如有必要）.

> 如果需要使用HTTPS，可以在外层新增一个HTTP网关（如Caddy），请参考后续章节。

### QuickStart

```bash

cp .env.example .env
docker-compose up

```

### Deployment

修改 `.env` 文件，设置下列参数：

- `BASE_DOMAIN`: 基础域名，如 `local.homeinfra.org`，镜像站将会使用 `*.local.homeinfra.org` 的子域名。
- `RPC_SECRET`：Aria2的RPC密钥。
- `all_proxy`：代理服务器地址，如有必要。
- `SCHEME`：`http` 或 `https`。

如果您需要HTTPS，请确保docker-compose.yml文件中开放443端口，并使用`cloudflare` 相关的Caddyfile和Dockerfile.

```bash
docker-compose up
```

测试命令：

```bash
docker pull docker.local.homeinfra.org/alpine
pip3 download -i http://pypi.local.homeinfra.org/simple/ jinja2 --trusted-host pypi.local.homeinfra.org
pip3 download -i http://torch.local.homeinfra.org/whl/ torch --trusted-host torch.local.homeinfra.org
```

## Design

LightMirrors依赖于两个组件：

- aria2 : 下载器与管理UI。
- mirrors: 镜像HTTP服务器，根据不同域名转发请求到不同模块。
  - Aria2Ng
  - PyPI
  - DockerHub
  - ...

## Test

> 假设我们的域名为 local.homeinfra.org

| subdomain | source                          | test command                                                      | test command (http)                                                                                      |
|-----------|---------------------------------|-------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------| 
| pypi      | https://pypi.org                | `pip3 download -i https://pypi.local.homeinfra.org/simple jinja2` | `pip3 download -i http://pypi.local.homeinfra.org/simple jinja2 --trusted-host pypi.local.homeinfra.org` | 
| torch     | https://download.pytorch.org    | `pip3 download -i https://torch.local.homeinfra.org/whl/ torch`   | `pip3 download -i http://torch.local.homeinfra.org/whl/ torch --trusted-host torch.local.homeinfra.org`  | 
| dockerhub | https://registry-1.docker.io/v2 | `docker pull docker.local.homeinfra.org/alpine`                   | `docker pull docker.local.homeinfra.org/alpine`                                                          |

## HTTPS

在 .env 中配置 `SCHEME=https` 与 CLOUDFLARE_DNS_API_TOKEN。
本项目提供了一个基于Cloudflare DNS的Caddyfile和Dockerfile，可以直接使用。如果您希望使用其他DNS Provider，请自行修改。

配置完成后，执行下列命令：

```bash
docker-compose -f docker-compose-caddy.yml up
```

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=NoCLin/LightMirrors&type=Date)](https://star-history.com/#NoCLin/LightMirrors&Date)

