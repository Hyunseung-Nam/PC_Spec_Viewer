# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/formatter.py

from __future__ import annotations

"""
수집된 시스템 사양 데이터를 사용자에게 보여줄 텍스트/HTML로 변환
클립보드 복사용 텍스트와 QTextEdit 표시용 HTML을 생성

- format_specs_text(): 클립보드 복사용 일반 텍스트 생성
- format_specs_html(): QTextEdit.setHtml()용 HTML 생성
- controller.py에서 호출되어 View에 표시될 형식으로 변환
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)
INFO_NOT_PROVIDED = "확인되지 않음(모듈 정보 미제공)"
NOT_INSTALLED = "장착되지 않음"
SYSTEM_TYPE_UNKNOWN = "유형 미확정"


def safe_str(value: Any) -> str:
    """
    값을 문자열로 변환
    
    None인 경우 "장착되지 않음"을 반환
    
    Args:
        value: 변환할 값
        
    Returns:
        str: 변환된 문자열 또는 "장착되지 않음"
    """
    if value is None:
        return NOT_INSTALLED
    return str(value).strip() or NOT_INSTALLED


def _format_system_type(value: Any) -> str:
    """
    시스템 유형 값을 안전하게 문자열로 변환한다.

    Args:
        value: 변환할 값

    Returns:
        str: 변환된 문자열 또는 "유형 미확정"
    """
    if value is None:
        return SYSTEM_TYPE_UNKNOWN
    text = str(value).strip()
    return text or SYSTEM_TYPE_UNKNOWN

def compress_items_xn(items: list[str]) -> list[str]:
    """
    동일한 문자열 항목을 묶어 'xN' 형식으로 압축하되,
    최초 등장 순서를 유지한다.

    예:
        ["A", "B", "A", "A"] → ["A x3", "B"]

    Args:
        items (list[str]):
            원본 항목 문자열 리스트
    Returns:
        list[str]:
            중복이 압축된 항목 리스트 (순서 유지)
    """

    cleaned = [s.strip() for s in items if s and s.strip()]

    counts: dict[str, int] = {}

    order: list[str] = []

    for s in cleaned:
        if s not in counts:
            counts[s] = 0
            order.append(s)

        counts[s] += 1

    out: list[str] = []
    for s in order:
        n = counts[s]
        out.append(f"{s} x{n}" if n > 1 else s)

    return out


def to_gb(bytes_value: int | float) -> float:
    """
    바이트 값을 GB로 변환
    
    Args:
        bytes_value: 바이트 단위 값
        
    Returns:
        float: GB 단위 값 (변환 실패 시 0.0)
    """
    try:
        return float(bytes_value) / (1024 ** 3)
    except (ValueError, TypeError):
        return 0.0


def format_ram_lines(ram_items: list[str]) -> str:
    """
    RAM 항목 리스트를 포맷팅된 텍스트로 변환
    
    Args:
        ram_items: RAM 정보 리스트
        
    Returns:
        str: 줄바꿈으로 구분된 텍스트 또는 "장착되지 않음"
    """
    if not ram_items:
        return NOT_INSTALLED
    return "\n".join(ram_items)


def format_storage_lines(storage_items: list[str]) -> str:
    """
    저장장치 항목 리스트를 포맷팅된 텍스트로 변환
    
    Args:
        storage_items: 저장장치 정보 리스트
        
    Returns:
        str: 줄바꿈으로 구분된 텍스트 또는 "장착되지 않음"
    """
    if not storage_items:
        return NOT_INSTALLED
    return "\n".join(storage_items)


def format_specs_text(specs: dict) -> str:
    """
    사양 딕셔너리를 일반 텍스트 형식으로 변환
    
    클립보드 복사용으로 CPU, RAM, M/B, VGA, SSD, HDD를
    읽기 쉬운 형식으로 포맷팅함
    
    Args:
        specs: collect_all_specs() 반환 형식의 딕셔너리
        
    Returns:
        str: 포맷팅된 텍스트 문자열
    """
    lines = []
    
    system_type = _format_system_type(specs.get("system_type"))
    lines.append(f"PC 유형 : {system_type}")
    lines.append("")
    lines.append(f"CPU : {safe_str(specs.get('cpu'))}")
    lines.append("")
    
    ram = specs.get('ram', [])
    if ram is None:
        lines.append(f"RAM : {INFO_NOT_PROVIDED}")
    elif ram:
        total_gb_text, ram_list = ram
        lines.append("RAM :")
        if total_gb_text and total_gb_text != NOT_INSTALLED:
            lines.append(f"  총 용량 : {total_gb_text}")
        if not ram_list:
            lines.append("  메인보드 내장 메모리 (온보드)")
        else:
            for item in ram_list:
                lines.append(f"  {item}")
    else:
        lines.append(f"RAM : {NOT_INSTALLED}")
    lines.append("")
    
    lines.append(f"M/B : {safe_str(specs.get('mainboard'))}")
    lines.append("")
    
    vga_items = specs.get('vga', [])
    if vga_items is None:
        lines.append(f"VGA : {INFO_NOT_PROVIDED}")
    elif vga_items:
        lines.append("VGA :")
        for vga in vga_items:
            lines.append(f"  {vga}")
    else:
        lines.append(f"VGA : {NOT_INSTALLED}")
    lines.append("")
    
    ssd_items = specs.get('ssd', [])
    if ssd_items is None:
        lines.append(f"SSD : {INFO_NOT_PROVIDED}")
    elif ssd_items:
        lines.append("SSD :")
        for ssd in ssd_items:
            lines.append(f"  {ssd}")
    else:
        lines.append(f"SSD : {NOT_INSTALLED}")
    lines.append("")
    
    hdd_items = specs.get('hdd', [])
    if hdd_items is None:
        lines.append(f"HDD : {INFO_NOT_PROVIDED}")
    elif hdd_items:
        lines.append("HDD :")
        for hdd in hdd_items:
            lines.append(f"  {hdd}")
    else:
        lines.append(f"HDD : {NOT_INSTALLED}")
    
    
    return "\n".join(lines)

def _render_single_row(label: str, value: str, add_sep: bool = True) -> str:
    """
    단일 항목의 HTML 행을 생성한다.

    Args:
        label: 좌측 라벨 텍스트
        value: 우측 값 텍스트
        add_sep: 구분선 행 추가 여부

    Returns:
        str: HTML 문자열
    """
    value = safe_str(value)
    sep = '<tr class="sep-row"><td colspan="2"></td></tr>' if add_sep else ""
    return f"""
<tr class="data-row">
  <td class="label">{label}</td>
  <td class="value">{value}</td>
</tr>
{sep}
"""


def _render_list_rows(label: str, items: list[str], add_sep: bool = True) -> str:
    """
    복수 항목의 HTML 행을 생성한다.

    Args:
        label: 좌측 라벨 텍스트
        items: 값 목록
        add_sep: 구분선 행 추가 여부

    Returns:
        str: HTML 문자열
    """
    if not items:
        items = [NOT_INSTALLED]

    rows = []
    rows.append(f"""
<tr class="data-row">
  <td class="label">{label}</td>
  <td class="value">{safe_str(items[0])}</td>
</tr>
""")

    for item in items[1:]:
        rows.append(f"""
<tr class="data-row">
  <td class="label empty">&nbsp;</td>
  <td class="value">{safe_str(item)}</td>
</tr>
""")

    if add_sep:
        rows.append('<tr class="sep-row"><td colspan="2"></td></tr>')

    return "\n".join(rows)


def build_spec_html(spec: dict, accent_color: str = "#B4B7CB5A") -> str:

    html = f"""<!DOCTYPE HTML>
<html>
<head>
<meta charset="utf-8"/>
<style>
body {{
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 12pt;
  color: #111827;
  background: transparent;
  margin: 2px;
  padding: 0;
  line-height: 1.12;
}}

table {{
  width: 100%;
  border-collapse: collapse;
}}

td {{
  padding: 0;
  vertical-align: top;
}}

td.label {{
  width: 64px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  padding-right: 10px;
}}

td.label.empty {{
  width: 64px;
}}

td.value {{
  font-weight: 400;
  color: #111827;
  white-space: normal;
  word-break: break-word;
}}

tr.sep-row td {{
  border-top: 1px solid {accent_color};
  height: 4px;
}}

.notice {{
  font-size: 10pt;
  color: #6b7280;
  padding-top: 6px;
  line-height: 1.3;
}}
</style>
</head>
<body>
<table>
"""

    system_type = _format_system_type(spec.get("system_type"))
    html += _render_single_row("PC 유형", system_type, add_sep=True)
    html += _render_single_row("CPU", spec.get("cpu"), add_sep=True)
    ram = spec.get("ram")
    if ram:
        total_str, ram_list = ram
        ram_list = compress_items_xn(ram_list)

        if not ram_list:
            ram_items = [f"총 용량 : {total_str}", "메인보드 내장 메모리 (온보드)"]
        else:
            ram_items = [f"총 용량 : {total_str}"] + ram_list
        html += _render_list_rows("RAM", ram_items, add_sep=True)
    else:
        html += _render_single_row("RAM", None, add_sep=True)
    html += _render_single_row("M/B", spec.get("mainboard"), add_sep=True)
    vga_items = spec.get("vga", [])
    if vga_items is None:
        vga_items = [INFO_NOT_PROVIDED]
    html += _render_list_rows("VGA", vga_items, add_sep=True)

    ssd_items = spec.get("ssd", [])
    if ssd_items is None:
        ssd_items = [INFO_NOT_PROVIDED]
    html += _render_list_rows("SSD", ssd_items, add_sep=True)

    hdd_items = spec.get("hdd", [])
    if hdd_items is None:
        hdd_items = [INFO_NOT_PROVIDED]
    html += _render_list_rows("HDD", hdd_items, add_sep=False)

    return html



def format_specs_html(specs: dict, accent_color: str = "#4b7bec") -> str:
    """
    사양 딕셔너리를 HTML 형식으로 변환
    
    build_spec_html()의 공개 API 별칭
    
    Args:
        specs: collect_all_specs() 반환 형식의 딕셔너리
        accent_color: 구분선 색상 (기본값: "#4b7bec")
        
    Returns:
        str: 완전한 HTML 문서 문자열
    """
    return build_spec_html(specs, accent_color)
