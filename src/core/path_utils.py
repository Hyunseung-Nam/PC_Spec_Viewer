# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/path_utils.py

from __future__ import annotations

"""
실행 시점의 경로(assets, logs 등)를 정의하는 유틸리티

- resource_base_dir(): 리소스 파일(이미지 등) 기준 경로
- runtime_base_dir(): 런타임 데이터(logs 등) 기준 경로
- logger.py, mainwindow_view.py에서 사용
"""

from pathlib import Path
import os
import sys
import platform

def user_data_dir(company: str, app_name: str, roaming: bool = False) -> Path:
    """
    OS 권장 사용자 데이터 경로 반환 (Windows 중심)
    
    - roaming=False: LocalAppData (로그/캐시등 대부분의 데이터)
    - roaming=True : RoamingAppData (설정/로밍이 필요한 데이터)
    """
    if platform.system() == "Windows":
        base = os.getenv("APPDATA") if roaming else os.getenv("LOCALAPPDATA")
        if not base:
            base = str(Path.home() / "AppData" / ("Roaming" if roaming else "Local"))
        return Path(base) / company / app_name

    return Path.home() / f".{app_name}"

def is_frozen() -> bool:
    """
    PyInstaller로 패키징되었는지 확인
    
    Returns:
        bool: 패키징된 경우 True, 개발 환경인 경우 False
    """
    return bool(getattr(sys, "frozen", False))

def resource_base_dir() -> Path:
    """
    리소스 파일(아이콘, 이미지 등) 기준 경로 반환
    
    PyInstaller onefile 환경에서는 _MEIPASS 임시 폴더를,
    개발 환경에서는 src 폴더를 반환합니다.
    
    Returns:
        Path: 리소스 파일 기준 디렉토리 경로
    """
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return _source_root_dir()


def resource_path(rel: str) -> Path:
    """
    상대 경로를 리소스 기준 경로로 변환
    
    Args:
        rel: 리소스 파일의 상대 경로 (예: "assets/logo.jpg")
        
    Returns:
        Path: 절대 경로
    """
    return resource_base_dir() / rel


def runtime_base_dir() -> Path:
    """
    실행(런타임) 기준 경로 반환
    
    런타임 데이터가 저장될 디렉토리를 반환
    패키징된 환경에서는 exe가 있는 폴더를,
    개발 환경에서는 src 폴더를 반환함
    
    Returns:
        Path: 런타임 데이터 기준 디렉토리 경로
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return _source_root_dir()


def _source_root_dir() -> Path:
    """
    개발 환경에서 소스 기준 루트 경로를 반환한다.

    Args:
        없음

    Returns:
        Path: 소스 루트 디렉토리 경로
    """
    return Path(__file__).resolve().parent.parent