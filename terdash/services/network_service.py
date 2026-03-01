"""Network speed tracking via psutil counters."""

import psutil


class NetworkSpeedTracker:
    """Tracks network speed by computing deltas between counter snapshots."""

    def __init__(self):
        counters = psutil.net_io_counters()
        self._last_bytes_sent = counters.bytes_sent
        self._last_bytes_recv = counters.bytes_recv

    def get_speed(self) -> dict:
        """Return current upload/download speed in bytes per second.

        Call this once per second for accurate results.
        """
        counters = psutil.net_io_counters()

        down = counters.bytes_recv - self._last_bytes_recv
        up = counters.bytes_sent - self._last_bytes_sent

        self._last_bytes_recv = counters.bytes_recv
        self._last_bytes_sent = counters.bytes_sent

        return {"down_bps": max(down, 0), "up_bps": max(up, 0)}


def format_speed(bps: float) -> str:
    """Format bytes-per-second into a human-readable string."""
    if bps < 1024:
        return f"{bps:.0f} B/s"
    elif bps < 1024 ** 2:
        return f"{bps / 1024:.1f} KB/s"
    elif bps < 1024 ** 3:
        return f"{bps / 1024 ** 2:.1f} MB/s"
    else:
        return f"{bps / 1024 ** 3:.2f} GB/s"
