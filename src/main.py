# main.py

from __future__ import annotations
import sys
import logging
from PySide6.QtWidgets import QApplication
from logger import setup_logging
from ui.mainwindow_view import MainWindow
from controller import Controller
from core.pathutils import runtime_base_dir

def main():
    app = QApplication(sys.argv)
    
    # 로거 설정
    log_dir = runtime_base_dir() / "logs"
    setup_logging(log_dir, level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("앱 시작")
    
    try:
        # View 객체 생성 (MainWindow)
        mainwindow_view = MainWindow()
        
        # Controller 객체 생성 및 View 연결
        controller = Controller(mainwindow_view)
        mainwindow_view.connect_controller(controller)
        
        # 실행 시 자동으로 사양 수집
        controller.init_auto_run()
        
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
