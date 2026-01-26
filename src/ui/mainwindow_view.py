# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
"""
메인 윈도우의 View를 구성하고 정적 리소스를 초기화한다.
다양한 실행 환경에서 UI 표시가 일관되게 유지되도록 보정한다.

- main.py에서 생성되어 Controller와 연결될 때 사용
- MainWindow.__init__()에서 UI 로드 및 창 설정 수행
"""

from __future__ import annotations

import logging
import re
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QIcon, QFont, QResizeEvent
from PyQt5.QtCore import Qt, QSize
from .ui_mainwindow import Ui_MainWindow

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    메인 윈도우의 UI를 구성하고 표시를 보정한다.

    - 책임: UI 위젯 구성, 정적 리소스 로드, 폰트/스케일 보정
    - 비책임: 사양 수집, 포맷팅, 이벤트 처리
    - 사용처: main.py에서 생성되어 Controller에 전달
    """
    def __init__(self):
        """
        메인 윈도우 UI를 초기화한다.

        Args:
            없음

        Returns:
            None
        """
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.resize(720, 820)
        
        self._base_window_size = QSize()
        self._base_dpi = 96.0
        self._font_scale_targets: list[dict] = []
        self._specs_html_base: str | None = None
        self._loading_overlay: QWidget | None = None
        self._loading_label: QLabel | None = None
        self._font_scale_excludes: set[QWidget] = set()
        self.ui.btnCopySpecs.setCursor(Qt.PointingHandCursor)
        
        self.setWindowTitle("PC 사양 확인 프로그램")

        self.ui.labelTitle.setMargin(0)

        self.ui.textSpecs.setReadOnly(True)
        self.ui.textSpecs.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.ui.textSpecs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._base_dpi = float(self.logicalDpiX())

        self._normalize_stylesheet_font_sizes(self._font_scale_widget_list())

        self._set_font_scale_excludes()

        self._base_window_size = self.size()
        self._font_scale_targets = self._build_font_scale_targets(
            self._font_scale_widget_list(include_sidebar=True)
        )

        logger.info("MainWindow 초기화 완료")
        


    def _normalize_stylesheet_font_sizes(self, widgets: list) -> None:
        """
        DPI 차이로 인한 폰트 크기 차이를 줄이기 위해 pt를 px로 변환한다.

        Args:
            widgets: font-size 스타일을 보정할 위젯 목록

        Returns:
            None
        """
        base_dpi = self._base_dpi
        for widget in widgets:
            style = widget.styleSheet()
            if not style:
                continue

            def _replace(match) -> str:
                pt_size = float(match.group(2))
                px_size = round(pt_size * base_dpi / 72)
                return f"{match.group(1)}{px_size}px"

            new_style = re.sub(
                r"(font-size\\s*:\\s*)(\\d+(?:\\.\\d+)?)pt",
                _replace,
                style,
                flags=re.IGNORECASE,
            )
            if new_style != style:
                widget.setStyleSheet(new_style)

    def _font_scale_widget_list(self, include_sidebar: bool = False) -> list[QWidget]:
        """
        폰트 스케일 보정 대상 위젯 목록을 반환한다.

        Args:
            include_sidebar: 사이드바 버튼 포함 여부

        Returns:
            list[QWidget]: 폰트 스케일 보정 대상 위젯 목록
        """
        widgets = [
            self.ui.labelTitle,
            self.ui.labelComment,
            self.ui.btnCopySpecs,
        ]
        return widgets

    def _set_font_scale_excludes(self) -> None:
        """
        폰트 스케일 제외 대상 위젯을 설정한다.

        Args:
            없음

        Returns:
            None
        """
        self._font_scale_excludes = set()

    def _build_font_scale_targets(self, widgets: list) -> list[dict]:
        """
        폰트 크기 비율 보정을 위한 기준 정보를 수집한다.

        Args:
            widgets: 폰트 크기 보정을 적용할 위젯 목록

        Returns:
            list[dict]: 위젯별 기준 폰트/스타일 정보 목록
        """
        targets = []
        base_dpi = self._base_dpi
        pattern = re.compile(r"(font-size\\s*:\\s*)(\\d+(?:\\.\\d+)?)(px|pt)", re.IGNORECASE)

        for widget in widgets:
            if widget in self._font_scale_excludes:
                continue
            style = widget.styleSheet()
            match = pattern.search(style or "")
            if match:
                size_value = float(match.group(2))
                unit = match.group(3).lower()
                base_px = size_value if unit == "px" else size_value * base_dpi / 72
                targets.append({
                    "widget": widget,
                    "base_px": base_px,
                    "style": style,
                    "use_style": True,
                })
                continue

            base_px = self._get_pixel_font_size(widget.font())
            targets.append({
                "widget": widget,
                "base_px": base_px,
                "style": "",
                "use_style": False,
            })

        return targets

    def _get_pixel_font_size(self, font: QFont) -> float:
        """
        폰트의 픽셀 크기를 반환한다.

        Args:
            font: 크기를 조회할 폰트

        Returns:
            float: 픽셀 단위 폰트 크기
        """
        if font.pixelSize() > 0:
            return float(font.pixelSize())
        point_size = font.pointSizeF()
        if point_size <= 0:
            return 12.0
        return point_size * self._base_dpi / 72

    def _apply_scaled_fonts(self, scale: float) -> None:
        """
        기준 폰트 크기에 스케일을 적용한다.

        Args:
            scale: 기준 대비 스케일 값

        Returns:
            None
        """
        pattern = re.compile(r"(font-size\\s*:\\s*)(\\d+(?:\\.\\d+)?)(px|pt)", re.IGNORECASE)

        for target in self._font_scale_targets:
            widget = target["widget"]
            base_px = target["base_px"]
            new_px = max(8, round(base_px * scale))
            if target["use_style"]:
                style = target["style"]
                new_style = pattern.sub(
                    lambda m: f"{m.group(1)}{new_px}px",
                    style,
                    count=1,
                )
                if new_style != widget.styleSheet():
                    widget.setStyleSheet(new_style)
            else:
                font = widget.font()
                font.setPixelSize(new_px)
                widget.setFont(font)

    def set_specs_html(self, html: str) -> None:
        """
        사양 표시 HTML을 저장하고 현재 크기에 맞춰 표시한다.

        Args:
            html: 기본 크기 기준의 HTML 문자열

        Returns:
            None
        """
        self._specs_html_base = html
        scale = self._compute_ui_scale()
        self._apply_scaled_specs_html(scale)

    def show_loading_overlay(self, message: str = "로딩 중입니다...") -> None:
        """
        초기 로딩용 오버레이를 표시한다.

        Args:
            message: 표시할 로딩 메시지

        Returns:
            None
        """
        if not self._loading_overlay:
            self._loading_overlay = QWidget(self.centralWidget())
            self._loading_overlay.setStyleSheet("background-color: #F5F7FA;")
            layout = QVBoxLayout(self._loading_overlay)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            self._loading_label = QLabel(message, self._loading_overlay)
            self._loading_label.setAlignment(Qt.AlignCenter)
            self._loading_label.setStyleSheet(
                "color: #2f2f2e; font-size: 14px; font-weight: 600;"
            )
            layout.addWidget(self._loading_label)

        if self._loading_label:
            self._loading_label.setText(message)
        self._update_loading_overlay_geometry()
        self._loading_overlay.show()
        self._loading_overlay.raise_()

    def hide_loading_overlay(self) -> None:
        """
        로딩 오버레이를 숨긴다.

        Args:
            없음

        Returns:
            None
        """
        if self._loading_overlay:
            self._loading_overlay.hide()

    def apply_font_refresh(self) -> None:
        """
        폰트 로딩 이후 기준 값을 재계산하고 UI를 갱신한다.

        Args:
            없음

        Returns:
            None
        """
        self._base_dpi = float(self.logicalDpiX())
        self._normalize_stylesheet_font_sizes(self._font_scale_widget_list())
        self._set_font_scale_excludes()
        self._base_window_size = self.size()
        self._font_scale_targets = self._build_font_scale_targets(
            self._font_scale_widget_list(include_sidebar=True)
        )
        self._apply_scaled_fonts(1.0)
        self._apply_scaled_specs_html(1.0)

    def _update_loading_overlay_geometry(self) -> None:
        """
        로딩 오버레이의 크기를 중앙 위젯에 맞춘다.

        Args:
            없음

        Returns:
            None
        """
        if not self._loading_overlay:
            return
        central = self.centralWidget()
        if central:
            self._loading_overlay.setGeometry(central.rect())

    def _apply_scaled_specs_html(self, scale: float) -> None:
        """
        HTML 폰트 크기를 스케일에 맞게 조정한다.

        Args:
            scale: 기준 대비 스케일 값

        Returns:
            None
        """
        if not self._specs_html_base:
            return

        def _replace(match: re.Match) -> str:
            base_pt = float(match.group(1))
            new_pt = max(8.0, round(base_pt * scale, 1))
            return f"font-size: {new_pt}pt"

        adjusted_html = re.sub(
            r"font-size\\s*:\\s*(\\d+(?:\\.\\d+)?)pt",
            _replace,
            self._specs_html_base,
            flags=re.IGNORECASE,
        )
        adjusted_html = f"""
        <div style="text-align:center;">
            {adjusted_html}
        </div>
        """
        self.ui.textSpecs.setHtml(adjusted_html)

    def _compute_ui_scale(self) -> float:
        """
        현재 창 크기와 DPI를 기준으로 스케일을 계산한다.

        Args:
            없음

        Returns:
            float: 현재 UI 스케일 값
        """
        scale = 1.0
        if self._base_window_size.width() > 0 and self._base_window_size.height() > 0:
            scale = min(
                self.width() / self._base_window_size.width(),
                self.height() / self._base_window_size.height(),
            )
        return scale * self._current_dpi_scale()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """
        창 크기 변경 시 폰트 비율을 유지한다.

        Args:
            event: 리사이즈 이벤트

        Returns:
            None
        """
        if self._base_window_size.width() > 0 and self._base_window_size.height() > 0:
            scale = self._compute_ui_scale()
            self._apply_scaled_fonts(scale)
            self._apply_scaled_specs_html(scale)

        self._update_loading_overlay_geometry()
        super().resizeEvent(event)

    def _current_dpi_scale(self) -> float:
        """
        현재 DPI 스케일을 기준 DPI 대비 비율로 계산한다.

        Args:
            없음

        Returns:
            float: 현재 DPI 스케일 비율
        """
        if self._base_dpi <= 0:
            return 1.0
        return float(self.logicalDpiX()) / self._base_dpi

