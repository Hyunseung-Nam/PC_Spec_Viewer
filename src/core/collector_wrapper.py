# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/collector_wrapper.py

"""
수집기 인터페이스 래퍼
기존 함수 기반 collector를 ISpecCollector 인터페이스에 맞게 래핑

- 책임: 함수 기반 collector를 객체 인터페이스로 변환
- 비책임: 실제 수집 로직 (기존 collector 함수에 위임)
- 사용처: CachedSpecCollector의 delegate로 사용
"""

from core.interfaces import ISpecCollector
from core import collector


class CollectorWrapper:
    """
    함수 기반 collector를 ISpecCollector 인터페이스로 래핑
    
    - 책임: ISpecCollector 인터페이스 구현
    - 비책임: 실제 수집 로직 (collector 모듈에 위임)
    - 사용처: CachedSpecCollector의 delegate로 사용
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
        return collector.collect_all_specs()


def _collect_specs_via_wrapper(wrapper: ISpecCollector) -> dict:
    """
    수집기 래퍼를 통해 사양을 수집한다.

    Args:
        wrapper: ISpecCollector 구현체

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
    return wrapper.collect_all_specs()

