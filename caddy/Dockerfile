FROM caddy:2.7.6-builder-alpine AS builder

# Optimization for China
RUN go env -w GOPROXY=https://goproxy.cn,direct

RUN xcaddy build \
    --with github.com/caddy-dns/cloudflare

FROM caddy:2.7.6-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy

RUN mkdir -p /wwwroot
WORKDIR /wwwroot

# Optimization for China as the project is aimed at Chinese users
ADD https://hub.gitmirror.com/https://github.com/mayswind/AriaNg/releases/download/1.3.7/AriaNg-1.3.7.zip /wwwroot/

RUN unzip AriaNg-1.3.7.zip && rm AriaNg-1.3.7.zip

ENTRYPOINT ["caddy"]

CMD ["run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]