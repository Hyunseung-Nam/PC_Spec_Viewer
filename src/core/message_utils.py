# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/message_utils.py

from __future__ import annotations

"""
QMessageBox를 표시하는 유틸리티 함수 모음
사용자에게 정보/경고/오류/확인 메시지를 표시

- show_information(), show_warning(), show_error(): 단순 메시지 표시
- ask_confirmation(): Yes/No 질문 (bool 반환)
- controller.py에서 예외 처리 및 사용자 알림에 사용
"""

from PyQt5.QtWidgets import QMessageBox, QWidget


def _show_message_box(
    method,
    parent_widget: QWidget,
    title: str,
    message: str,
) -> None:
    """
    QMessageBox 표시 공통 로직을 수행한다.

    Args:
        method: QMessageBox 표시 메서드
        parent_widget: 부모 위젯
        title: 메시지 박스 제목
        message: 표시할 메시지

    Returns:
        None
    """
    method(parent_widget, title, message, QMessageBox.Ok)


def show_warning(parent_widget: QWidget, title: str, message: str):
    """
    경고 메시지 표시
    
    Args:
        parent_widget: 부모 위젯
        title: 메시지 박스 제목
        message: 표시할 메시지
    """
    _show_message_box(QMessageBox.warning, parent_widget, title, message)

def show_information(parent_widget: QWidget, title: str, message: str):
    """
    정보 메시지 표시
    
    Args:
        parent_widget: 부모 위젯
        title: 메시지 박스 제목
        message: 표시할 메시지
    """
    _show_message_box(QMessageBox.information, parent_widget, title, message)

def ask_confirmation(parent_widget: QWidget, title: str, question: str) -> bool:
    """
    확인 질문 표시
    
    Args:
        parent_widget: 부모 위젯
        title: 메시지 박스 제목
        question: 질문 내용
        
    Returns:
        bool: Yes 클릭 시 True, No 클릭 시 False
    """
    result = QMessageBox.question(
        parent_widget, title, question,
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No 
    )
    return result == QMessageBox.Yes

def show_error(parent_widget: QWidget, title: str, message: str):
    """
    오류 메시지 표시
    
    Args:
        parent_widget: 부모 위젯
        title: 메시지 박스 제목
        message: 표시할 오류 메시지
    """
    _show_message_box(QMessageBox.critical, parent_widget, title, message)