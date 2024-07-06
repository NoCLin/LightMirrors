set -ex

cat /scripts/certs/certificate.crt >> /etc/ssl/certs/ca-certificates.crt

pip config set global.index-url https://pypi.local.homeinfra.org/simple
 pip config set global.trusted-host pypi.local.homeinfra.org
pip download jinja2 --dest /tmp/pypi/


pip config set global.index-url https://torch.local.homeinfra.org/whl
pip config set global.trusted-host torch.local.homeinfra.org
pip download tqdm --dest /tmp/torch/