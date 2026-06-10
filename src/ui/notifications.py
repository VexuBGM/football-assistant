from nicegui import ui

from ..utils.logger import log_command


ERROR_MARKERS = (
    "error",
    "invalid",
    "no ",
    "not ",
    "cannot",
    "failed",
    "already",
    "internal",
)


def is_error_message(message: str) -> bool:
    normalized = message.strip().lower()
    return normalized.startswith(ERROR_MARKERS) or " failed" in normalized


def notify_result(message: str) -> None:
    ui.notify(
        message,
        type="negative" if is_error_message(message) else "positive",
        position="top-right",
        close_button=True,
        multi_line=True,
    )


def notify_and_log(raw_input: str, intent: str, params: dict, result: str) -> None:
    log_command(raw_input, intent, params, result)
    notify_result(result)
