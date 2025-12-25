# core/message_utils.py

from PySide6.QtWidgets import QMessageBox
from PySide6.QtWidgets import QWidget

def show_warning(parent_widget: QWidget, title: str, message: str):
    """경고 메시지 실행"""
    QMessageBox.warning(parent_widget, title, message, QMessageBox.Ok)

def show_information(parent_widget: QWidget, title: str, message: str):
    """정보 메시지 실행"""
    QMessageBox.information(parent_widget, title, message, QMessageBox.Ok)

def ask_confirmation(parent_widget: QWidget, title: str, question: str) -> bool:
    """확인 질문 실행 (True/False 반환)"""
    result = QMessageBox.question(
        parent_widget, title, question,
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No 
    )
    return result == QMessageBox.Yes

def show_error(parent_widget: QWidget, title: str, message: str):
    """치명적/비정상 오류"""
    QMessageBox.critical(parent_widget, title, message, QMessageBox.Ok)