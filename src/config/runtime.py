"""Runtime Environment Detection & Auto-Fallback Manager.

Determines whether AETHER-DC operates in:
1. Docker Compose Mode (Redpanda Kafka Broker + FastAPI + External Prometheus)
2. Cloud Demo Fallback Mode (In-Memory Ring-Buffer + In-Process Prometheus Registry)
Ensures 100% zero-crash operation on Streamlit Community Cloud.
"""

from enum import Enum
import os
from pathlib import Path
import socket
from typing import Dict, Any
import yaml


class RuntimeMode(str, Enum):
    DOCKER_KAFKA = "Docker Kafka Broker"
    CLOUD_STREAM = "In-Process Cloud Stream"


def _is_port_open(host: str, port: int, timeout_sec: float = 0.5) -> bool:
    """Checks whether a TCP socket port is reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout_sec):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def get_base_dir() -> Path:
    """Returns the project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def load_settings() -> Dict[str, Any]:
    """Loads settings.yaml configuration file."""
    config_path = get_base_dir() / "config" / "settings.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def detect_runtime_mode() -> RuntimeMode:
    """Detects active runtime mode based on environment variables and socket checks."""
    force_cloud = os.getenv("AETHER_FORCE_CLOUD", "false").lower() in ("true", "1", "yes")
    if force_cloud:
        return RuntimeMode.CLOUD_STREAM

    # Check if running in Streamlit Community Cloud
    is_cloud_env = (
        "STREAMLIT_SHARING_MODE" in os.environ
        or "STREAMLIT_SERVER_PORT" in os.environ and not os.path.exists("/.dockerenv")
    )

    # Check Kafka broker availability
    kafka_broker = os.getenv("REDPANDA_BROKERS", "localhost:9092")
    try:
        parts = kafka_broker.split(":")
        host = parts[0]
        port = int(parts[1]) if len(parts) > 1 else 9092
        broker_reachable = _is_port_open(host, port, timeout_sec=0.3)
    except Exception:
        broker_reachable = False

    if broker_reachable and not is_cloud_env:
        return RuntimeMode.DOCKER_KAFKA
    return RuntimeMode.CLOUD_STREAM


def get_duckdb_path() -> Path:
    """Resolves absolute path to DuckDB database file."""
    env_path = os.getenv("DUCKDB_PATH")
    if env_path:
        p = Path(env_path)
    else:
        p = get_base_dir() / "data" / "lakehouse" / "aether_dc.duckdb"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def get_models_dir() -> Path:
    """Resolves path to serialized model directory."""
    p = get_base_dir() / "data" / "models"
    p.mkdir(parents=True, exist_ok=True)
    return p

