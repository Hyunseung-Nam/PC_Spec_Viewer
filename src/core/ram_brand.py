# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
"""
SPD 없이 RAM 브랜드를 추론하는 규칙을 제공한다.
WMI/SMBIOS 문자열과 PartNumber 패턴으로 보수적으로 판정하기 위해 존재한다.

- Windows WMI Win32_PhysicalMemory 수집 결과를 보정할 때 사용된다.
- core.collector에서 RAM 표기용 브랜드 문자열 생성에 사용된다.
"""

from __future__ import annotations

import re
from enum import Enum


class RamBrand(str, Enum):
    """
    RAM 브랜드 표기를 위한 열거형.

    - 책임: 표준화된 브랜드 문자열 제공
    - 비책임: 제조사 문자열 파싱/추론
    - 사용처: core.ram_brand, core.collector
    """

    SAMSUNG = "Samsung"
    SK_HYNIX = "SK hynix"
    MICRON = "Micron"
    KINGSTON = "Kingston"
    ADATA = "ADATA"
    UNKNOWN = "Unknown"


INVALID_MANUFACTURERS = {"", "unknown", "0000", "0", "null", "na", "n/a"}


def _normalize_text(value: str | None) -> str:
    """
    문자열을 소문자/공백/특수기호 제거 형태로 정규화한다.

    Args:
        value: 정규화할 문자열 (None 가능)

    Returns:
        str: 소문자/특수기호 제거된 문자열
    """
    if not value:
        return ""
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _is_invalid_manufacturer(value: str | None) -> bool:
    """
    의미 없는 Manufacturer 값을 걸러낸다.

    Args:
        value: Manufacturer 문자열 (None 가능)

    Returns:
        bool: 무의미한 Manufacturer이면 True
    """
    if not value:
        return True
    stripped = value.strip().lower()
    if stripped in INVALID_MANUFACTURERS:
        return True
    return re.fullmatch(r"[0-9a-f]{4}", stripped) is not None


def _detect_by_manufacturer(manufacturer: str | None) -> RamBrand | None:
    """
    Manufacturer 기반 확정 판별.

    Args:
        manufacturer: Manufacturer 문자열 (None 가능)

    Returns:
        RamBrand | None: 확정 브랜드 또는 None
    """
    if _is_invalid_manufacturer(manufacturer):
        return None

    norm = _normalize_text(manufacturer)
    if "samsung" in norm:
        return RamBrand.SAMSUNG
    if "skhynix" in norm or "hynix" in norm:
        return RamBrand.SK_HYNIX
    if "micron" in norm or "crucial" in norm:
        return RamBrand.MICRON
    if "kingston" in norm:
        return RamBrand.KINGSTON
    return None


def _detect_by_part_number(part_number: str | None) -> RamBrand | None:
    """
    PartNumber 기반 보조 판별(heuristic).

    Args:
        part_number: PartNumber 문자열 (None 가능)

    Returns:
        RamBrand | None: 추론된 브랜드 또는 None
    """
    if not part_number:
        return None

    pn = part_number.strip().upper()

    # Micron heuristic
    if re.match(r"^M(T|TA|PT)[0-9A-Z]", pn):
        return RamBrand.MICRON  # heuristic

    # Kingston heuristic
    if re.match(r"^(KVR|KF)[0-9A-Z]", pn):
        return RamBrand.KINGSTON  # heuristic
    if re.match(r"^99[0-9]{5}", pn):
        return RamBrand.KINGSTON  # heuristic

    # ADATA heuristic (보수적)
    if re.match(r"^AD[23][0-9A-Z]", pn):
        return RamBrand.ADATA  # heuristic
    if re.match(r"^AX[34]U[0-9A-Z]", pn):
        return RamBrand.ADATA  # heuristic

    # TODO: ADATA 추가 패턴/내부 코드 매핑 확장 포인트
    return None


def detect_ram_brand(manufacturer: str | None, part_number: str | None) -> RamBrand:
    """
    RAM 브랜드 최종 판별.
    Manufacturer 우선 → PartNumber heuristic → Unknown.

    Args:
        manufacturer: Manufacturer 문자열 (None 가능)
        part_number: PartNumber 문자열 (None 가능)

    Returns:
        RamBrand: 최종 브랜드
    """
    brand = _detect_by_manufacturer(manufacturer)
    if brand:
        return brand

    brand = _detect_by_part_number(part_number)
    if brand:
        return brand

    return RamBrand.UNKNOWN


def resolve_ram_brand_display(manufacturer: str | None, part_number: str | None) -> str:
    """
    UI 표기용 브랜드 문자열을 반환한다.

    Args:
        manufacturer: Manufacturer 문자열 (None 가능)
        part_number: PartNumber 문자열 (None 가능)

    Returns:
        str: UI 표기용 브랜드 문자열
    """
    brand = detect_ram_brand(manufacturer, part_number)
    if brand != RamBrand.UNKNOWN:
        return brand.value
    if _is_invalid_manufacturer(manufacturer):
        return RamBrand.UNKNOWN.value
    return (manufacturer or "").strip() or RamBrand.UNKNOWN.value
