# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# main.py

from __future__ import annotations

"""
애플리케이션 진입점
QApplication 생성, View/Controller 초기화, 이벤트 루프 시작을 담당함

- main() 함수에서 앱 전체 생명주기 관리
- logger 설정 및 예외 처리
"""
import sys
import logging
import ctypes
from PyQt5.QtWidgets import QApplication
from logger import setup_logging
from ui.mainwindow_view import MainWindow
from controller import Controller
from core.path_utils import user_data_dir
from core.font_utils import apply_app_font

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def main():
    """
    애플리케이션 진입점
    
    로깅 설정 → QApplication 생성 → View/Controller 초기화 → 이벤트 루프 시작
    예외 발생 시 전체 스택 트레이스를 로깅하고 앱 종료
    """
    
    log_dir = user_data_dir(company="NanoMemory", app_name="PC_Spec_Viewer") / "logs"
    setup_logging(log_dir, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("앱 시작")
    logger.info(f"관리자 권한 실행 여부: {is_admin()}")
    
    try:
        app = QApplication(sys.argv)
        mainwindow_view = MainWindow()
        mainwindow_view.show_loading_overlay()
        mainwindow_view.show()
        app.processEvents()

        apply_app_font()
        mainwindow_view.apply_font_refresh()
        controller = Controller(mainwindow_view)
        mainwindow_view.hide_loading_overlay()
        
        exit_code = app.exec_()
        logger.info("앱 종료")
        sys.exit(exit_code)
    except Exception:
        logger.exception("앱 비정상 종료")
        raise

if __name__ == "__main__":
    main()
