set -ex

cat /scripts/certs/certificate.crt >> /etc/ssl/certs/ca-certificates.crt

go env -w GOPROXY=https://goproxy.local.homeinfra.org,direct

go clean -modcache
go mod init test
go get golang.org/x/sys@v0.22.0
