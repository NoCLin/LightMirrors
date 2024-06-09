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


class SetupMirrors():
    def __enter__(self):
        os.chdir(root_dir)
        call("docker-compose up -d")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        call("docker-compose down")
        os.chdir(test_dir)
        return False
