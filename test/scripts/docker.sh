set -ex
export DOCKER_HOST=unix:///var/run/docker.sock

cat /scripts/certs/certificate.crt >> /etc/ssl/certs/ca-certificates.crt

dockerd&

docker_ready() {
  docker version >/dev/null 2>&1
}

max_wait_time=5
elapsed_time=0

# Wait for Docker to be ready
while [ true ]; do
  if docker_ready; then
    echo "Docker is ready!"
    break
  else
    echo "Waiting for Docker to start..."
    sleep 1
    elapsed_time=$((elapsed_time + 1))
    if [ $elapsed_time -gt $max_wait_time ]; then
      echo "Docker failed to start in $max_wait_time seconds!"
      exit 1
  fi
  fi
done

docker pull docker.local.homeinfra.org/busybox
docker pull ghcr.local.homeinfra.org/linuxcontainers/alpine
docker pull quay.local.homeinfra.org/quay/busybox
docker pull k8s.local.homeinfra.org/pause

# https is required
echo 'FROM docker.local.homeinfra.org/alpine' | docker build -
