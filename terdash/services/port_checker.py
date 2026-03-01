"""TCP port checker and runtime version detector for service health monitoring."""

import asyncio
import re
import shutil
import socket
import subprocess


def check_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open (blocking)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, TimeoutError, OSError):
        return False


def get_runtime_version(command: str) -> str | None:
    """Run a version command and return a cleaned version string, or None if unavailable.

    Uses shutil.which to resolve the executable full path, avoiding
    shell=True issues on Windows where PATH may differ in sub-shells.
    """
    parts = command.split()
    exe = shutil.which(parts[0])
    if exe is None:
        return None

    try:
        result = subprocess.run(
            [exe] + parts[1:],
            capture_output=True,
            timeout=5,
        )
        if result.returncode != 0:
            return None
        output = (result.stdout + result.stderr).decode("utf-8", errors="ignore").strip()
        if not output:
            return None
        m = re.search(r'"([\d][\d.]*)"', output) or re.search(r"[v ](\d+[\.\d]*\.\d+)", output) or re.search(r"(\d+[\.\d]+)", output)
        if m:
            return m.group(1)
        # Single number version like Java "21"
        m = re.search(r"(\d+)", output)
        return m.group(1) if m else output.split("\n")[0][:40]
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


async def check_port_async(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open (async)."""
    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        return True
    except (ConnectionRefusedError, TimeoutError, OSError, asyncio.TimeoutError):
        return False
