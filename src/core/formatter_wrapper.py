# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/formatter_wrapper.py

"""
포맷터 인터페이스 래퍼
기존 함수 기반 formatter를 ISpecFormatter 인터페이스에 맞게 래핑

- 책임: 함수 기반 formatter를 객체 인터페이스로 변환
- 비책임: 실제 포맷팅 로직 (기존 formatter 함수에 위임)
- 사용처: Controller에서 ISpecFormatter 구현체로 주입
"""

from core.interfaces import ISpecFormatter
from core import formatter


class FormatterWrapper:
    """
    함수 기반 formatter를 ISpecFormatter 인터페이스로 래핑
    
    - 책임: ISpecFormatter 인터페이스 구현
    - 비책임: 실제 포맷팅 로직 (formatter 모듈에 위임)
    - 사용처: Controller에서 의존성 주입으로 사용
    """
    
    def format_specs_text(self, specs: dict) -> str:
        """
        사양 딕셔너리를 일반 텍스트 형식으로 변환
        
        Args:
            specs: collect_all_specs() 반환 형식의 딕셔너리
            
        Returns:
            str: 포맷팅된 텍스트 문자열
        """
        return formatter.format_specs_text(specs)
    
    def format_specs_html(self, specs: dict, accent_color: str = "#4b7bec") -> str:
        """
        사양 딕셔너리를 HTML 형식으로 변환
        
        Args:
            specs: collect_all_specs() 반환 형식의 딕셔너리
            accent_color: 구분선 색상 (기본값: "#4b7bec")
            
        Returns:
            str: 완전한 HTML 문서 문자열
        """
        return formatter.format_specs_html(specs, accent_color)

