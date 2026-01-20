# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# navigation.py
from PyQt5.QtCore import QObject, QPropertyAnimation, QEasingCurve, pyqtSlot
from PyQt5.QtWidgets import QButtonGroup, QGraphicsOpacityEffect, QStackedWidget


class NavigationController(QObject):
    """
    - 버튼 클릭 시 QStackedWidget 페이지 전환
    - 전환 시 부드러운 페이드(현재 페이지 fade-out -> 다음 페이지 fade-in)
    - 버튼 4개/페이지 4개 같은 구조에 최적
    """

    def __init__(
        self,
        stack: QStackedWidget,
        buttons: list,
        parent=None,
        fade_ms: int = 180,
        keep_active_checked: bool = True
    ):
        super().__init__(parent)
        self.stack = stack
        self.buttons = buttons
        self.fade_ms = fade_ms
        self.keep_active_checked = keep_active_checked

        self._anim_out = None
        self._anim_in = None
        self._is_animating = False
        self._pending_index = None

        # 1) 버튼 그룹 (exclusive)
        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        for i, b in enumerate(self.buttons):
            # 버튼이 checkable이 아니면 활성 유지가 안 되므로 켜줌
            if self.keep_active_checked:
                b.setCheckable(True)
            self.group.addButton(b, i)

        # 2) 클릭 -> 전환
        self.group.idClicked.connect(self.set_index_animated)

        # 3) 초기 상태
        if self.buttons:
            if self.keep_active_checked:
                self.buttons[0].setChecked(True)
            self.stack.setCurrentIndex(0)

    @pyqtSlot(int)
    def set_index_animated(self, target_index: int):
        if target_index < 0 or target_index >= self.stack.count():
            return

        if self._is_animating:
            # 애니메이션 도중 재클릭하면 마지막 요청만 반영
            self._pending_index = target_index
            return

        current_index = self.stack.currentIndex()
        if target_index == current_index:
            return

        current_w = self.stack.currentWidget()
        next_w = self.stack.widget(target_index)

        # (선택) active 체크 유지: 클릭된 버튼만 checked가 되게
        if self.keep_active_checked:
            btn = self.group.button(target_index)
            if btn is not None:
                btn.setChecked(True)

        self._is_animating = True

        # 1) 현재 위젯 fade-out
        eff_out = current_w.graphicsEffect()
        if not isinstance(eff_out, QGraphicsOpacityEffect):
            eff_out = QGraphicsOpacityEffect(current_w)
            current_w.setGraphicsEffect(eff_out)
        eff_out.setOpacity(1.0)

        self._anim_out = QPropertyAnimation(eff_out, b"opacity", self)
        self._anim_out.setDuration(self.fade_ms)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.setEasingCurve(QEasingCurve.OutCubic)

        def after_out():
            # 2) 페이지 전환
            self.stack.setCurrentIndex(target_index)

            # 3) 다음 위젯 fade-in
            eff_in = next_w.graphicsEffect()
            if not isinstance(eff_in, QGraphicsOpacityEffect):
                eff_in = QGraphicsOpacityEffect(next_w)
                next_w.setGraphicsEffect(eff_in)
            eff_in.setOpacity(0.0)

            self._anim_in = QPropertyAnimation(eff_in, b"opacity", self)
            self._anim_in.setDuration(self.fade_ms)
            self._anim_in.setStartValue(0.0)
            self._anim_in.setEndValue(1.0)
            self._anim_in.setEasingCurve(QEasingCurve.OutCubic)

            def after_in():
                self._is_animating = False
                # 혹시 도중에 다른 index 요청이 들어왔으면 이어서 처리
                if self._pending_index is not None:
                    idx = self._pending_index
                    self._pending_index = None
                    self.set_index_animated(idx)

            self._anim_in.finished.connect(after_in)
            self._anim_in.start()

        self._anim_out.finished.connect(after_out)
        self._anim_out.start()
