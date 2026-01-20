# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/interfaces.py

"""
인터페이스 정의 모듈
SOLID 원칙의 ISP(Interface Segregation)와 DIP(Dependency Inversion)를 준수하기 위한 추상 인터페이스

- ISpecCollector: 시스템 사양 수집 인터페이스
- ISpecFormatter: 사양 데이터 포맷팅 인터페이스
- 성능 최적화 구현체는 이 인터페이스를 구현하여 기존 코드와 호환

- controller.py에서 인터페이스에 의존하여 구현체 교체 가능
- core/collector.py, core/formatter.py는 기본 구현체로 유지
"""

try:
    from typing import Protocol
except ImportError:
    from typing_extensions import Protocol


class ISpecCollector(Protocol):
    """
    시스템 사양 수집 인터페이스
    
    - 책임: 시스템 사양 수집 메서드 정의
    - 비책임: 실제 수집 로직 구현 (구현체에서 담당)
    - 사용처: Controller에서 의존성 주입으로 사용
    """
    
    def collect_all_specs(self) -> dict:
        """
        모든 시스템 사양을 수집하여 딕셔너리로 반환
        
        Returns:
            dict: {
                "cpu": str,
                "ram": tuple[list[str], str],
                "mainboard": str,
                "vga": list[str],
                "ssd": list[str],
                "hdd": list[str]
            }
        """
        ...


class ISpecFormatter(Protocol):
    """
    사양 데이터 포맷팅 인터페이스
    
    - 책임: 사양 데이터 포맷팅 메서드 정의
    - 비책임: 실제 포맷팅 로직 구현 (구현체에서 담당)
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
        ...
    
    def format_specs_html(self, specs: dict, accent_color: str = "#4b7bec") -> str:
        """
        사양 딕셔너리를 HTML 형식으로 변환
        
        Args:
            specs: collect_all_specs() 반환 형식의 딕셔너리
            accent_color: 구분선 색상 (기본값: "#4b7bec")
            
        Returns:
            str: 완전한 HTML 문서 문자열
        """
        ...
