FROM alpine:3.19.1

RUN apk update && apk add --no-cache aria2

ADD ./entrypoint.sh /
ADD ./aria2.conf /

EXPOSE 6800

CMD ["/entrypoint.sh"]