# core/pathutils.py

from __future__ import annotations
from pathlib import Path
import sys

def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))

def find_project_root(start: Path) -> Path:
    for p in [start, *start.parents]:
        if (p / "README.md").exists() or (p / ".gitignore").exists() or (p / "requirements.txt").exists():
            return p
    return start.parents[0]

def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent  # exe 있는 폴더
    return find_project_root(Path(__file__).resolve()) # 프로젝트 폴더


# 리소스(아이콘, qss, 이미지 등) 기준 경로
def resource_base_dir() -> Path:
    # PyInstaller onefile이면 _MEIPASS(임시폴더)에 리소스가 풀림
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    # onedir / dev 환경: src 폴더 기준
    return Path(__file__).resolve().parent.parent


def resource_path(rel: str) -> Path:
    return resource_base_dir() / rel


# 실행(런타임) 기준 경로: "항상 exe가 있는 폴더"
#   - data는 여기에 둬야 onefile에서도 안정적임
def runtime_base_dir() -> Path:
    if is_frozen():
        return Path(sys.executable).resolve().parent
    # 개발 환경에서는 프로젝트 구조에 맞게 선택
    # 지금 __file__이 src/pathutils.py라면, src 폴더를 런타임 기준으로 두는 게 기존과 일치
    return Path(__file__).resolve().parent


# def data_dir() -> Path:
#     return runtime_base_dir() / "data"


# def ensure_data_dir_or_exit(data_path: Path | None = None) -> None:
#     """
#     data 폴더가 없으면 새로 만들지 말고 경고 후 종료
#     """
#     if data_path is None:
#         data_path = data_dir()

#     if data_path.exists() and data_path.is_dir():
#         return

#     msg = QMessageBox()
#     msg.setIcon(QMessageBox.Critical)
#     msg.setWindowTitle("데이터 폴더를 찾을 수 없습니다")
#     msg.setText("프로그램 데이터(data) 폴더가 없어 실행을 중단합니다.")
#     msg.setInformativeText(
#         "업데이트 적용 시에는 기존 프로그램 폴더에 exe를 덮어써서 사용하거나,\n"
#         "바탕화면에서 사용하셨다면 바탕화면의 data 폴더를 프로그램 폴더로 함께 옮겨주세요.\n\n"
#         f"찾는 위치: {str(data_path)}"
#     )

#     open_btn = msg.addButton("프로그램 폴더 열기", QMessageBox.ActionRole)
#     msg.addButton("종료", QMessageBox.RejectRole)

#     msg.exec()

#     if msg.clickedButton() == open_btn:
#         QDesktopServices.openUrl(QUrl.fromLocalFile(str(data_path.parent)))

#     QApplication.quit()
#     sys.exit(1)