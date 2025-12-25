# controller.py

from __future__ import annotations
import logging
from PySide6.QtCore import QUrl, Qt
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QApplication
from core.collector import collect_all_specs
from core.formatter import format_specs_text, format_specs_html
from core.message_utils import show_error, show_information
from core.pathutils import resource_path

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, view):
        self.view = view
        self.current_specs = None
        self.bind_signals()
        self.load_images()
    
    def bind_signals(self):
        """UI 위젯의 시그널을 이벤트 핸들러에 연결합니다."""
        # 버튼 클릭 이벤트 연결
        self.view.ui.btnCopySpecs.clicked.connect(self.on_copy_specs_clicked)
        self.view.ui.btnOpenHomepage.clicked.connect(self.on_open_board_clicked)
        self.view.ui.btnOpenKakao.clicked.connect(self.on_open_kakao_clicked)
        
        logger.info("시그널 바인딩 완료")
    
    def load_images(self):
        """로고 및 QR 코드 이미지를 로드합니다."""
        try:
            # 로고 이미지
            logo_path = resource_path("assets/out-nano-logo.jpg")
            if logo_path.exists():
                pixmap = QPixmap(str(logo_path))
                self.view.ui.labelLogo.setPixmap(pixmap.scaled(
                    self.view.ui.labelLogo.width(),
                    self.view.ui.labelLogo.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            
            # QR 코드 이미지
            qr_path = resource_path("assets/qrcode_600.png")
            if qr_path.exists():
                pixmap = QPixmap(str(qr_path))
                self.view.ui.labelQR.setPixmap(pixmap.scaled(
                    self.view.ui.labelQR.width(),
                    self.view.ui.labelQR.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
        except Exception as e:
            logger.warning(f"이미지 로드 실패: {e}")
    
    def init_auto_run(self):
        """실행 시 자동으로 사양을 수집하고 표시합니다."""
        try:
            logger.info("자동 사양 수집 시작")
            specs = collect_all_specs()
            self.current_specs = specs
            self.render_specs(specs)
            logger.info("자동 사양 수집 완료")
        except Exception as e:
            self.handle_error(e)
    
    def on_load_specs_clicked(self):
        """사양 수집 버튼 클릭 이벤트 핸들러."""
        try:
            logger.info("사양 수집 버튼 클릭")
            specs = collect_all_specs()
            self.current_specs = specs
            self.render_specs(specs)
            show_information(self.view, "완료", "PC 사양 수집이 완료되었습니다.")
        except Exception as e:
            self.handle_error(e)
    
    def on_copy_specs_clicked(self):
        """PC 사양 복사 버튼 클릭 이벤트 핸들러."""
        try:
            if not self.current_specs:
                show_information(
                    self.view,
                    "알림",
                    "먼저 PC 사양을 수집해주세요."
                )
                return
            
            # 텍스트 형식으로 변환
            text = format_specs_text(self.current_specs)
            
            # 클립보드에 복사
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            show_information(
                self.view,
                "완료",
                "PC 사양이 클립보드에 복사되었습니다."
            )
            logger.info("PC 사양 클립보드 복사 완료")
        except Exception as e:
            self.handle_error(e)
    
    def on_open_board_clicked(self):
        """홈페이지 매입 견적 문의 게시판 버튼 클릭 이벤트 핸들러."""
        try:
            url = QUrl("https://www.nanomemory.co.kr/purchase/inquiry.php?ptype=input&mode=insert&code=inquiry&pos=&code_page=purchase")
            QDesktopServices.openUrl(url)
            logger.info("홈페이지 열기: %s", url.toString())
        except Exception as e:
            self.handle_error(e)
    
    def on_open_kakao_clicked(self):
        """카카오톡 문의 바로가기 버튼 클릭 이벤트 핸들러."""
        try:
            url = QUrl("http://pf.kakao.com/_xfwxmSxd")
            QDesktopServices.openUrl(url)
            logger.info("카카오톡 채널 열기: %s", url.toString())
        except Exception as e:
            self.handle_error(e)
    
    def render_specs(self, specs: dict):
        """
        수집된 사양을 UI에 표시합니다.
        
        Args:
            specs: 사양 딕셔너리
        """
        try:
            # HTML 형식으로 변환
            html = format_specs_html(specs)
            
            # QTextEdit에 HTML 설정
            self.view.ui.textSpecs.setHtml(html)
            
            # 읽기 전용 설정
            self.view.ui.textSpecs.setReadOnly(True)
            
            logger.info("사양 렌더링 완료")
        except Exception as e:
            logger.exception("사양 렌더링 실패")
            self.handle_error(e)
    
    def handle_error(self, exc: Exception):
        """
        예외를 처리합니다.
        전체 스택 트레이스를 로거에 기록하고,
        사용자에게는 짧고 친절한 메시지를 표시합니다.
        
        Args:
            exc: 발생한 예외
        """
        # 전체 스택 트레이스를 로거에 기록
        logger.exception("오류 발생: %s", str(exc))
        
        # 사용자에게는 짧고 친절한 메시지 표시
        error_message = "PC 사양 수집 중 오류가 발생했습니다.\n\n"
        error_message += "외장형 저장장치(SSD, HDD, USB)를 제거한 후\n"
        error_message += "다시 시도해주세요."
        
        show_error(self.view, "오류", error_message)
