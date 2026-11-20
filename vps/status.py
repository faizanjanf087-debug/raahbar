from vps import ssh

STATUS_COMMAND = "uptime; df -h /; free -m"


def check(vps_id):
    """Read-only status: bina approval ke chalta hai."""
    result = ssh.run(vps_id, STATUS_COMMAND)
    return result["stdout"] or result["stderr"]
