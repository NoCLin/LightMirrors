FROM alpine:3.19.1

# Optimization for China
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories

RUN apk update && apk add --no-cache aria2

ADD entrypoint.sh /
ADD aria2.conf /

EXPOSE 6800

CMD ["/entrypoint.sh"]