"""Global configuration for TerDash."""

# Refresh intervals (seconds)
REFRESH_FAST = 1        # CPU, memory, network
REFRESH_MEDIUM = 10     # Service health
REFRESH_SLOW = 300      # GitHub contributions (5 min)

# GitHub settings
GITHUB_USERNAME = "octocat"
GITHUB_TOKEN = ""  # Set via env var GITHUB_TOKEN for real data

# Services to monitor — (name, host, port)
MONITORED_SERVICES = [
    ("PostgreSQL", "127.0.0.1", 5432),
    ("Redis", "127.0.0.1", 6379),
    ("MySQL", "127.0.0.1", 3306),
    ("RabbitMQ", "127.0.0.1", 5672),
    ("Nginx", "127.0.0.1", 80),
]

# Runtime environments to check — (name, version_command)
MONITORED_RUNTIMES = [
    ("Java", "java -version"),
    ("Python", "python --version"),
    ("Node.js", "node --version"),
    ("Go", "go version"),
]

# Network speed display
SPEED_UNITS = ["B/s", "KB/s", "MB/s", "GB/s"]
