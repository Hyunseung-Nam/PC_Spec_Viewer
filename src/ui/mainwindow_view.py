# ui/mainwindow_view.py

from __future__ import annotations
import logging
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon
from .ui_mainwindow import Ui_MainWindow
from core.pathutils import resource_path

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # UI 로드
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # 창 설정
        self.setWindowTitle("나노메모리 PC 사양 확인 프로그램")
        
        # 윈도우 아이콘 설정 (상단바 아이콘)
        icon_path = resource_path("assets/out-nano-logo_blue.jpg")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # QTextEdit 읽기 전용 설정
        self.ui.textSpecs.setReadOnly(True)
        
        logger.info("MainWindow 초기화 완료")
    
    def connect_controller(self, controller_instance):
        """
        View가 주도적으로 자신의 버튼을 Controller의 메서드에 연결합니다.
        """
        # Controller에서 bind_signals()를 호출하므로 여기서는 로그만 남김
        logger.info("MainWindow connected to Controller: %s", controller_instance.__class__.__name__)
