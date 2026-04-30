from pathlib import Path
import uuid

from src.utils import logger


def _log_path() -> Path:
    log_dir = Path(".test_dbs")
    log_dir.mkdir(exist_ok=True)
    return log_dir / f"commands-{uuid.uuid4().hex}.log"


def test_log_command_marks_stage6_validation_failure_as_error(monkeypatch):
    log_path = _log_path()
    monkeypatch.setattr(logger.os.path, "abspath", lambda _: str(log_path))

    try:
        logger.log_command(
            "goal Ivan Petrov Aster 0",
            "add_goal",
            {"subject": "Ivan Petrov Aster", "minute": 0},
            "Minute must be between 1 and 120.",
        )

        contents = log_path.read_text(encoding="utf-8")
        assert "RESULT: ERROR | Minute must be between 1 and 120." in contents
    finally:
        if log_path.exists():
            log_path.unlink()


def test_log_command_keeps_successful_stage6_command_as_ok(monkeypatch):
    log_path = _log_path()
    monkeypatch.setattr(logger.os.path, "abspath", lambda _: str(log_path))

    try:
        logger.log_command(
            "goal Ivan Petrov Aster 23",
            "add_goal",
            {"subject": "Ivan Petrov Aster", "minute": 23},
            "Goal added: Ivan Petrov for Aster in minute 23 (match #1, goal #1).",
        )

        contents = log_path.read_text(encoding="utf-8")
        assert "RESULT: OK | Goal added: Ivan Petrov for Aster in minute 23 (match #1, goal #1)." in contents
    finally:
        if log_path.exists():
            log_path.unlink()
