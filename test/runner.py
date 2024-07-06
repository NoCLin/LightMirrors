#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

test_dir = Path(__file__).parent
root_dir = Path(__file__).parent.parent


def call(cmd):
    print(f">>  {cmd}")
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = p.communicate()
    assert p.returncode == 0, f"Error: {stderr.decode()}"
    print(">>", stdout.decode())
    return stdout.decode(), stderr.decode()


services = [
    "python_test",
    "docker_test",
    "golang_test"
]

os.chdir(root_dir)

if not os.path.exists(".env"):
    call("cp .env.example .env")
call("docker-compose up -d --force-recreate --wait")

os.chdir(test_dir)

try:
    for service in services:
        call(f'docker-compose up --force-recreate --exit-code-from {service} {service}')
except Exception as e:
    raise e
finally:
    os.chdir(root_dir)
    call("docker-compose down")
