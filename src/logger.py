# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# logger.py

from __future__ import annotations

"""
애플리케이션 전역 로깅 설정
RotatingFileHandler를 사용하여 로그 파일 관리

- setup_logging()에서 로그 디렉토리 생성 및 핸들러 설정
- main.py에서 앱 시작 시 호출
- 중복 설정 방지 로직 포함
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_dir: Path, level: int = logging.INFO) -> None:
    """
    애플리케이션 전역 로깅 설정
    
    RotatingFileHandler를 사용하여 최대 2MB, 백업 3개까지 유지
    이미 핸들러가 설정되어 있으면 중복 설정을 방지
    
    Args:
        log_dir: 로그 파일이 저장될 디렉토리 경로
        level: 로깅 레벨 (default: logging.INFO)
    """
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