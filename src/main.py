# main.py

from __future__ import annotations
import sys, logging
from logger import setup_logging
from PySide6.QtWidgets import QApplication
from core.pathutils import resource_path
from core.formatter import ensure_files_exist, migrate_users_phone_keys_once
from ui.mainwindow_view import MainWindow
from controller import Controller

def main():
    app = QApplication(sys.argv)

    # 로거 설정
    setup_logging("log", level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("앱 시작")

    # 파일 / 데이터 준비
    try:
        ensure_files_exist()
        migrate_users_phone_keys_once()

        # View 객체 생성 (MainWindow)
        mainwindow_view = MainWindow()
        
        # Controller 객체 생성 및 View 연결
        controller = Controller(mainwindow_view)
        mainwindow_view.connect_controller(controller)
        
        # 화면 표시 및 이벤트 루프 시작
        mainwindow_view.show()
        
        exit_code = app.exec()
        logger.info("앱 종료")
        sys.exit(exit_code)
    except Exception:
        logger.exception("앱 비정상 종료")
        raise

if __name__ == "__main__":
    main()