import io

import paramiko

from vps import registry


def run(vps_id, command, timeout=20):
    vps = registry.get_vps(vps_id)
    key = paramiko.PKey.from_private_key(io.StringIO(vps["key"]))
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(vps["host"], username=vps["user"], pkey=key, timeout=timeout)
        _, stdout, stderr = client.exec_command(command, timeout=timeout)
        out = stdout.read().decode(errors="replace")
        err = stderr.read().decode(errors="replace")
        code = stdout.channel.recv_exit_status()
        return {"stdout": out, "stderr": err, "exit_code": code}
    finally:
        client.close()
