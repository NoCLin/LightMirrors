<div style="text-align: center">

# LightMirrors

LightMirrors是一个开源的缓存镜像站服务，用于加速软件包下载和镜像拉取。
目前支持DockerHub、PyPI、PyTorch、NPM等镜像缓存服务。


<a href='https://github.com/NoCLin/LightMirrors/'><img src='https://img.shields.io/badge/Light-Mirrors-green'></a>
<a href='https://github.com/homeinfra-org/infra'><img src='https://img.shields.io/static/v1?label=Home&message=Infra&color=orange'></a> 
[![GitHub](https://img.shields.io/github/stars/NoCLin/LightMirrors?style=social)](https://github.com/NoCLin/LightMirrors)
[![GitHub](https://img.shields.io/github/forks/NoCLin/LightMirrors?style=social)](https://github.com/NoCLin/LightMirrors)

</div>


---

## Quick Start

### Prerequisites

- docker + docker-compose.
- 一个域名，设置 `*.local.homeinfra.org` 的A记录指向您的服务器.
- 代理服务器（如有必要）.
- 一个Cloudflare账户（非强制，也可以使用其他DNS服务，请自行修改Caddy）

### Deployment

修改 `.env` 文件，设置下列参数：

- `BASE_DOMAIN`: 基础域名，如 `local.homeinfra.org`，镜像站将会使用 `*.local.homeinfra.org` 的子域名。
- `CLOUDFLARE_DNS_API_TOKEN`，Cloudflare的API Token，用于管理DNS申请HTTPS证书。
- `RPC_SECRET`：Aria2的RPC密钥。
- `all_proxy`：代理服务器地址，如有必要。

```bash
docker-compose up
```

## Design

LightMirrors依赖于三个组件：

- aria2 + Aria2Ng : 下载器与管理UI。
- mirrors: 镜像HTTP服务器。
- caddy: HTTP网关。

## Test

> 假设我们的域名为 local.homeinfra.org

| subdomain | source                          | test command                                                    |
|-----------|---------------------------------|-----------------------------------------------------------------|
| pypi      | https://pypi.org                | pip3 download -i https://pypi.local.homeinfra.org/simple jinja2 |
| torch     | https://download.pytorch.org    | pip3 download -i https://torch.local.homeinfra.org/whl/ torch   |
| dockerhub | https://registry-1.docker.io/v2 | docker pull docker.local.homeinfra.org/alpine                   |


## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=NoCLin/LightMirrors&type=Date)](https://star-history.com/#NoCLin/LightMirrors&Date)

