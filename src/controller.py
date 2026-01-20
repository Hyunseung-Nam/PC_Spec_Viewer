# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# controller.py

from __future__ import annotations

"""
View와 데이터 수집/포맷팅 로직을 연결하는 컨트롤러
UI 이벤트 처리, 사양 수집/표시, 클립보드 복사, 외부 링크 열기를 담당함

- Controller.__init__()에서 View와 연결 및 초기 사양 수집
- UI 버튼 클릭 이벤트를 이벤트 핸들러로 라우팅
- collector/formatter를 호출하여 View 업데이트
- SOLID 원칙 준수: 인터페이스에 의존하여 구현체 교체 가능
"""
import logging
from typing import Optional
from PyQt5.QtWidgets import QApplication
from core.interfaces import ISpecCollector, ISpecFormatter
from core.collector_wrapper import CollectorWrapper
from core.formatter_wrapper import FormatterWrapper
from core.message_utils import show_error, show_information

logger = logging.getLogger(__name__)


class Controller:
    """
    UI 이벤트 처리 및 데이터 흐름 제어
    
    - 책임: UI 시그널 바인딩, 사양 수집/렌더링, 클립보드 복사, 외부 링크 열기, 예외 처리
    - 비책임: 실제 사양 수집(collector), 데이터 포맷팅(formatter), UI 위젯 생성(View)
    - 사용처: main.py에서 View와 함께 생성
    """
    def __init__(self, view, 
                 spec_collector: Optional[ISpecCollector] = None,
                 spec_formatter: Optional[ISpecFormatter] = None):
        """
        Controller 초기화
        
        Args:
            view: MainWindow 인스턴스
            spec_collector: 사양 수집기 구현체 (기본값: CollectorWrapper)
            spec_formatter: 사양 포맷터 구현체 (기본값: FormatterWrapper)
        """
        self.view = view
        self.current_specs: Optional[dict] = None
        
        # 의존성 주입 (DIP 준수)
        if spec_collector is None:
            spec_collector = CollectorWrapper()
        if spec_formatter is None:
            spec_formatter = FormatterWrapper()
        
        self._spec_collector = spec_collector
        self._spec_formatter = spec_formatter
        
        self.bind_signals()
        self.load_specs()
    
    def bind_signals(self):
        """
        UI 위젯의 시그널을 이벤트 핸들러에 연결
        
        btnCopySpecs 버튼 클릭 이벤트를 핸들러에 연결
        """
        # 버튼 클릭 이벤트 연결
        self.view.ui.btnCopySpecs.clicked.connect(self.on_copy_specs_clicked)
        
        logger.info("시그널 바인딩 완료")

    def load_specs(self):
        """
        실행 시 자동으로 사양을 수집하고 표시
        
        spec_collector를 호출하여 시스템 사양을 수집하고,
        render_specs()로 UI에 표시함
        예외 발생 시 handle_error()로 처리
        """
        try:
            logger.info("자동 사양 수집 시작")
            specs = self._spec_collector.collect_all_specs()
            self.current_specs = specs
            self.render_specs(specs)
            logger.info("자동 사양 수집 완료")
        except Exception as e:
            self.handle_error(e)
    
    def on_copy_specs_clicked(self):
        """
        PC 사양 복사 버튼 클릭 이벤트 핸들러
        
        current_specs가 없으면 사용자에게 알림을 표시하고,
        있으면 format_specs_text()로 텍스트 변환 후 클립보드에 복사
        """
        try:
            if not self.current_specs:
                show_information(
                    self.view,
                    "알림",
                    "먼저 PC 사양을 수집해주세요."
                )
                return
            
            text = self._spec_formatter.format_specs_text(self.current_specs)
            
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            
            show_information(
                self.view,
                "복사 완료",
                "PC 사양이 클립보드에 복사되었습니다."
            )
            logger.info("PC 사양 클립보드 복사 완료")
        except Exception as e:
            show_error(
            self.view,
            "오류",
            "PC 사양을 클립보드에 복사하지 못했습니다.\n\n"
            "보안 설정 또는 원격/가상 환경으로 인해 클립보드 접근이 제한되었을 수 있습니다.\n"
            "문제가 계속되면 담당자에게 문의해주세요.")
            self.handle_error(e)
    
    def render_specs(self, specs: dict):
        """
        수집된 사양을 UI에 표시
        
        format_specs_html()로 HTML 변환 후 QTextEdit.setHtml()로 UI에 표시
        
        Args:
            specs: 사양 딕셔너리 (collect_all_specs() 반환 형식)
        """
        try:
            html = self._spec_formatter.format_specs_html(specs)
            self.view.set_specs_html(html)
            
            logger.info("사양 렌더링 완료")
        except Exception as e:
            logger.exception("사양 렌더링 실패")
            self.handle_error(e)
    
    def handle_error(self, exc: Exception):
        """
        예외 처리
        전체 스택 트레이스를 로거에 기록하고,
        사용자에게 오류 메시지를 표시
        
        Args:
            exc: 발생한 예외
        """
        # 전체 스택 트레이스를 로거에 기록
        logger.exception("오류 발생: %s", str(exc))
        
        # 사용자에게 오류 메시지 표시
        error_message = "PC 사양 수집 중 오류가 발생했습니다.\n\n"
        error_message += f"원인: {exc}\n\n"
        error_message += "다시 시도해주세요."
        
        show_error(self.view, "오류", error_message)
