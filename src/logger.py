# logger.py

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: Path, level: int = logging.INFO) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    root = logging.getLogger()
    if root.handlers:  # 이미 설정돼 있으면 중복 설정 방지
        return

    root.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_path, 
        maxBytes=2_000_000, 
        backupCount=3, 
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)