# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
"""
앱 전체 폰트를 로드하고 기본 폰트를 설정한다.
다양한 실행 환경에서 동일한 폰트가 적용되도록 보장한다.

- main.py의 apply_app_font()에서 호출되어 전체 UI에 적용
- assets/fonts의 Noto Sans KR 폰트를 로드하여 사용
"""

from __future__ import annotations

import logging
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication
from core.path_utils import resource_path

logger = logging.getLogger(__name__)


def _load_font_family(rel_path: str) -> list[str]:
    """
    지정된 폰트 파일을 로드하고 폰트 패밀리 목록을 반환한다.

    Args:
        rel_path: 리소스 기준 폰트 파일 상대 경로

    Returns:
        list[str]: 로드된 폰트 패밀리 목록
    """
    font_path = resource_path(rel_path)
    if not font_path.exists():
        logger.warning(f"폰트 파일이 없습니다: {font_path}")
        return []

    font_id = QFontDatabase.addApplicationFont(str(font_path))
    if font_id < 0:
        logger.warning(f"폰트 로드 실패: {font_path}")
        return []

    return QFontDatabase.applicationFontFamilies(font_id)


def apply_app_font() -> None:
    """
    애플리케이션 기본 폰트를 로드하고 적용한다.

    폰트 로드 실패 시 시스템 기본 폰트로 동작한다.

    Args:
        없음

    Returns:
        None
    """
    regular_families = _load_font_family("assets/fonts/NotoSansKR-Regular.ttf")
    _load_font_family("assets/fonts/NotoSansKR-Bold.ttf")

    family = _select_font_family(regular_families)

    app = QApplication.instance()
    if not app:
        logger.warning("QApplication 인스턴스를 찾지 못했습니다.")
        return

    font = QFont(family)
    font.setPointSize(12)
    app.setFont(font)


def _select_font_family(regular_families: list[str]) -> str:
    """
    적용할 폰트 패밀리를 선택한다.

    Args:
        regular_families: 로드된 폰트 패밀리 목록

    Returns:
        str: 적용할 폰트 패밀리
    """
    if regular_families:
        return regular_families[0]
    return "Noto Sans KR"
