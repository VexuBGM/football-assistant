import json
import os
from datetime import datetime
from typing import Any


def _looks_like_error(message: str) -> bool:
    lowered = message.lower()
    error_prefixes = (
        "error",
        "invalid",
        "no ",
        "cannot",
        "transfer failed",
        "delete failed",
        "internal error",
        "i did not understand",
    )
    return lowered.startswith(error_prefixes)


def _format_params(params: dict[str, Any]) -> str:
    return json.dumps(params, ensure_ascii=False, separators=(",", ":"))


def log_command(raw_input: str, intent: str, params: dict[str, Any], result: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "commands.log"))
    status = "ERROR" if _looks_like_error(result) else "OK"

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] INPUT: {raw_input}\n")
        log_file.write(f"[{timestamp}] INTENT: {intent}\n")
        log_file.write(f"[{timestamp}] PARAMS: {_format_params(params)}\n")
        log_file.write(f"[{timestamp}] RESULT: {status} | {result}\n")
        log_file.write("-" * 60 + "\n")
