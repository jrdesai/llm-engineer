"""
Centralized Logging Configuration

WHY this exists as a separate file instead of inside router.py or main.py:
  - router.py, main.py, and any future modules all need logging
  - If each file calls logging.basicConfig(), they conflict and only the first one wins
  - One place to change format, level, and output destination for the whole app

WHY JSON format instead of plain text:
  Plain text: "2026-03-21 10:00:01 - INFO - Classical: URGENT (conf=0.85)"
  JSON:       {"timestamp": "...", "level": "INFO", "category": "URGENT", "confidence": 0.85, "latency_ms": 2.1}

  With JSON you can query logs like a database:
    - "show me all LLM calls that took > 2 seconds"
    - "show me all URGENT tickets from the last hour"
    - "what is the p95 latency for classical routing?"
  Any log aggregator (Datadog, Grafana, CloudWatch) can do this automatically with JSON.
  With plain text, you'd have to write custom regex parsers.
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    Formats every log record as a single-line JSON string.

    Standard log fields (level, message, logger name) are always included.
    Any extra fields passed via extra={...} are merged in automatically.

    Example usage:
        logger.info("routing_decision", extra={
            "method": "CLASSICAL",
            "category": "URGENT",
            "confidence": 0.85,
            "latency_ms": 2.1
        })

    Produces:
        {"timestamp": "2026-03-21T10:00:01Z", "level": "INFO",
         "logger": "router", "message": "routing_decision",
         "service": "task-router", "method": "CLASSICAL",
         "category": "URGENT", "confidence": 0.85, "latency_ms": 2.1}
    """

    # Fields that are internal to Python's logging machinery — never include in JSON output
    _INTERNAL_FIELDS = {
        "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
        "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
        "created", "msecs", "relativeCreated", "thread", "threadName",
        "processName", "process", "message", "taskName",
    }

    def format(self, record: logging.LogRecord) -> str:
        # Base fields always present in every log line
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "task-router",
        }

        # Append exception traceback if one was logged
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Merge in any extra fields passed at the call site
        # e.g. logger.info("msg", extra={"request_id": "abc", "latency_ms": 45})
        for key, value in record.__dict__.items():
            if key not in self._INTERNAL_FIELDS:
                log_entry[key] = value

        return json.dumps(log_entry)


def setup_logging(
    level: Optional[str] = None,
    log_file: Optional[str] = None,
    json_format: Optional[bool] = None,
) -> None:
    """
    Configure logging for the entire application. Call this ONCE at startup in main.py.

    All loggers created anywhere in the app with logging.getLogger(__name__)
    automatically inherit this configuration — you don't need to configure
    each file individually.

    WHY force=True in basicConfig?
        router.py currently calls logging.basicConfig() at import time.
        Without force=True, the first basicConfig() call wins and ignores ours.
        force=True overrides any prior setup so our config always takes effect.

    Args:
        level:       Log level ("DEBUG", "INFO", "WARNING", "ERROR").
                     Falls back to LOG_LEVEL env var, then "INFO".
        log_file:    Path to write logs to a file (e.g. "logs/app.log").
                     Falls back to LOG_FILE env var, then console-only.
        json_format: True = JSON output, False = human-readable text.
                     Falls back to LOG_FORMAT env var ("json"/"text"), then JSON.
    """
    # --- Resolve settings (argument > env var > default) ---

    resolved_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, resolved_level, logging.INFO)

    if json_format is None:
        json_format = os.getenv("LOG_FORMAT", "json").lower() != "text"

    resolved_log_file = log_file or os.getenv("LOG_FILE")

    # --- Build formatter ---

    if json_format:
        formatter = JSONFormatter()
    else:
        # Human-readable: useful for local dev (set LOG_FORMAT=text)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # --- Build handlers ---

    # Console handler — always present so logs appear in terminal and Docker logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers: list[logging.Handler] = [console_handler]

    # File handler — optional, useful in Docker (mount ./logs:/app/logs)
    if resolved_log_file:
        log_dir = os.path.dirname(resolved_log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(resolved_log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # --- Apply to root logger (all child loggers inherit this) ---
    logging.basicConfig(
        level=numeric_level,
        handlers=handlers,
        force=True,  # Override any basicConfig already called (e.g. in router.py)
    )

    # --- Silence noisy third-party libraries ---
    # uvicorn logs every HTTP request in its own format — we handle that in main.py
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # httpx is used internally by some Google SDK calls — suppress debug noise
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Confirm setup worked
    logger = logging.getLogger(__name__)
    logger.info(
        "Logging initialized",
        extra={
            "log_level": resolved_level,
            "format": "json" if json_format else "text",
            "log_file": resolved_log_file or "console only",
        },
    )
