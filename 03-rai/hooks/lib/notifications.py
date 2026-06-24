"""Notification service: ntfy + Discord + Twilio."""

import json
import subprocess
from pathlib import Path

from .identity import get_notification_config

# Default config. Override in settings.json under "notifications".
DEFAULT_CONFIG = {
    "ntfy": {
        "enabled": False,
        "server": "https://ntfy.sh",
        "topic": "",  # SET YOUR TOPIC
    },
    "discord": {
        "enabled": False,
        "webhook_url": "",  # SET YOUR WEBHOOK
    },
    "twilio": {
        "enabled": False,
        "account_sid": "",  # SET YOUR SID
        "auth_token": "",   # SET YOUR TOKEN
        "from_number": "",  # SET YOUR NUMBER
        "to_number": "",    # SET YOUR NUMBER
    },
    "routing": {
        "task_complete": ["ntfy"],
        "long_task": ["ntfy"],
        "background_agent": ["ntfy"],
        "error": ["ntfy", "discord"],
        "security": ["ntfy", "discord"],
    },
}


def _get_config() -> dict:
    """Get merged notification config."""
    user_config = get_notification_config()
    if user_config:
        return {**DEFAULT_CONFIG, **user_config}
    return DEFAULT_CONFIG


def _send_ntfy(title: str, message: str, priority: str = "default"):
    """Send push via ntfy.sh."""
    config = _get_config().get("ntfy", {})
    if not config.get("enabled") or not config.get("topic"):
        return
    try:
        server = config.get("server", "https://ntfy.sh")
        topic = config["topic"]
        subprocess.Popen(
            [
                "curl", "-s",
                "-H", f"Title: {title}",
                "-H", f"Priority: {priority}",
                "-d", message,
                f"{server}/{topic}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def _send_discord(title: str, message: str):
    """Send via Discord webhook."""
    config = _get_config().get("discord", {})
    if not config.get("enabled") or not config.get("webhook_url"):
        return
    try:
        payload = json.dumps({
            "content": f"**{title}**\n{message}",
        })
        subprocess.Popen(
            [
                "curl", "-s",
                "-H", "Content-Type: application/json",
                "-d", payload,
                config["webhook_url"],
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def _send_twilio(message: str):
    """Send SMS via Twilio."""
    config = _get_config().get("twilio", {})
    required = ["account_sid", "auth_token", "from_number", "to_number"]
    if not config.get("enabled"):
        return
    if not all(config.get(k) for k in required):
        return
    try:
        sid = config["account_sid"]
        token = config["auth_token"]
        subprocess.Popen(
            [
                "curl", "-s", "-X", "POST",
                f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                "-u", f"{sid}:{token}",
                "--data-urlencode", f"From={config['from_number']}",
                "--data-urlencode", f"To={config['to_number']}",
                "--data-urlencode", f"Body={message}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        pass


def notify(
    event: str,
    title: str,
    message: str,
    priority: str = "default",
):
    """
    Send notification based on event routing.
    Events: task_complete, long_task, background_agent, error, security.
    """
    config = _get_config()
    channels = config.get("routing", {}).get(event, [])

    for channel in channels:
        if channel == "ntfy":
            _send_ntfy(title, message, priority)
        elif channel == "discord":
            _send_discord(title, message)
        elif channel == "twilio":
            _send_twilio(f"{title}: {message}")
