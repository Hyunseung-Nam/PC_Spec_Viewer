# core/formatter.py

from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


def safe_str(value: Any) -> str:
    """값을 안전하게 문자열로 변환합니다."""
    if value is None:
        return "정보 없음"
    return str(value).strip() or "정보 없음"


def to_gb(bytes_value: int | float) -> float:
    """바이트 값을 GB로 변환합니다."""
    try:
        return float(bytes_value) / (1024 ** 3)
    except (ValueError, TypeError):
        return 0.0


def format_ram_lines(ram_items: list[str]) -> str:
    """RAM 항목 리스트를 포맷팅된 텍스트로 변환합니다."""
    if not ram_items:
        return "정보 없음"
    return "\n".join(ram_items)


def format_storage_lines(storage_items: list[str]) -> str:
    """저장장치 항목 리스트를 포맷팅된 텍스트로 변환합니다."""
    if not storage_items:
        return "정보 없음"
    return "\n".join(storage_items)


def format_specs_text(specs: dict) -> str:
    """
    사양 딕셔너리를 일반 텍스트 형식으로 변환합니다.
    (클립보드 복사용)
    """
    lines = []
    
    lines.append(f"CPU : {safe_str(specs.get('cpu', '정보 없음'))}")
    lines.append("")
    
    ram_items = specs.get('ram', [])
    if ram_items:
        lines.append("RAM :")
        for ram in ram_items:
            lines.append(f"  {ram}")
    else:
        lines.append("RAM : 정보 없음")
    lines.append("")
    
    lines.append(f"M/B : {safe_str(specs.get('mainboard', '정보 없음'))}")
    lines.append("")
    
    vga_items = specs.get('vga', [])
    if vga_items:
        lines.append("VGA :")
        for vga in vga_items:
            lines.append(f"  {vga}")
    else:
        lines.append("VGA : 정보 없음")
    lines.append("")
    
    ssd_items = specs.get('ssd', [])
    if ssd_items:
        lines.append("SSD :")
        for ssd in ssd_items:
            lines.append(f"  {ssd}")
    else:
        lines.append("SSD : 정보 없음")
    lines.append("")
    
    hdd_items = specs.get('hdd', [])
    if hdd_items:
        lines.append("HDD :")
        for hdd in hdd_items:
            lines.append(f"  {hdd}")
    else:
        lines.append("HDD : 정보 없음")
    
    return "\n".join(lines)


def build_spec_html(spec: dict, accent_color: str = "#2F80ED") -> str:
    """
    사양 딕셔너리를 HTML 형식으로 변환합니다.
    QTextEdit.setHtml()에 사용할 수 있는 HTML을 생성합니다.
    
    Args:
        spec: 사양 딕셔너리
        accent_color: 강조 색상 (기본값: #2F80ED)
    
    Returns:
        HTML 문자열
    """
    html_parts = []
    
    # HTML 헤더 및 스타일
    html_parts.append("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">")
    html_parts.append("<html><head><meta charset=\"utf-8\"/>")
    html_parts.append("<style type=\"text/css\">")
    html_parts.append("body {")
    html_parts.append("  font-family: 'Segoe UI', '맑은 고딕', 'Malgun Gothic', sans-serif;")
    html_parts.append("  font-size: 11pt;")
    html_parts.append("  color: #000000;")
    html_parts.append("  background-color: #F9FAFB;")
    html_parts.append("  margin: 12px;")
    html_parts.append("  line-height: 1.6;")
    html_parts.append("}")
    html_parts.append(".section-title {")
    html_parts.append(f"  font-weight: bold;")
    html_parts.append("  font-size: 12pt;")
    html_parts.append("  color: #000000;")
    html_parts.append("  margin-top: 16px;")
    html_parts.append("  margin-bottom: 8px;")
    html_parts.append("}")
    html_parts.append(".section-content {")
    html_parts.append("  font-weight: normal;")
    html_parts.append("  font-size: 11pt;")
    html_parts.append("  color: #333;")
    html_parts.append("  margin-left: 0px;")
    html_parts.append("  margin-bottom: 12px;")
    html_parts.append("  white-space: pre-wrap;")
    html_parts.append("}")
    html_parts.append(".divider {")
    html_parts.append(f"  border-bottom: 1px solid {accent_color};")
    html_parts.append("  margin: 12px 0;")
    html_parts.append("  height: 0;")
    html_parts.append("}")
    html_parts.append("</style>")
    html_parts.append("</head><body>")
    
    # CPU 섹션
    cpu = safe_str(spec.get('cpu', '정보 없음'))
    html_parts.append("<div class=\"section-title\">CPU</div>")
    html_parts.append(f"<div class=\"section-content\">{cpu}</div>")
    html_parts.append("<div class=\"divider\"></div>")
    
    # RAM 섹션
    ram_items = spec.get('ram', [])
    html_parts.append("<div class=\"section-title\">RAM</div>")
    if ram_items:
        ram_html = "<br/>".join([safe_str(ram) for ram in ram_items])
        html_parts.append(f"<div class=\"section-content\">{ram_html}</div>")
    else:
        html_parts.append("<div class=\"section-content\">정보 없음</div>")
    html_parts.append("<div class=\"divider\"></div>")
    
    # M/B 섹션
    mainboard = safe_str(spec.get('mainboard', '정보 없음'))
    html_parts.append("<div class=\"section-title\">M/B</div>")
    html_parts.append(f"<div class=\"section-content\">{mainboard}</div>")
    html_parts.append("<div class=\"divider\"></div>")
    
    # VGA 섹션
    vga_items = spec.get('vga', [])
    html_parts.append("<div class=\"section-title\">VGA</div>")
    if vga_items:
        vga_html = "<br/>".join([safe_str(vga) for vga in vga_items])
        html_parts.append(f"<div class=\"section-content\">{vga_html}</div>")
    else:
        html_parts.append("<div class=\"section-content\">정보 없음</div>")
    html_parts.append("<div class=\"divider\"></div>")
    
    # SSD 섹션
    ssd_items = spec.get('ssd', [])
    html_parts.append("<div class=\"section-title\">SSD</div>")
    if ssd_items:
        ssd_html = "<br/>".join([safe_str(ssd) for ssd in ssd_items])
        html_parts.append(f"<div class=\"section-content\">{ssd_html}</div>")
    else:
        html_parts.append("<div class=\"section-content\">정보 없음</div>")
    html_parts.append("<div class=\"divider\"></div>")
    
    # HDD 섹션
    hdd_items = spec.get('hdd', [])
    html_parts.append("<div class=\"section-title\">HDD</div>")
    if hdd_items:
        hdd_html = "<br/>".join([safe_str(hdd) for hdd in hdd_items])
        html_parts.append(f"<div class=\"section-content\">{hdd_html}</div>")
    else:
        html_parts.append("<div class=\"section-content\">정보 없음</div>")
    
    html_parts.append("</body></html>")
    
    return "\n".join(html_parts)


def format_specs_html(specs: dict, accent_color: str = "#2F80ED") -> str:
    """
    사양 딕셔너리를 HTML 형식으로 변환합니다.
    build_spec_html()의 별칭입니다.
    """
    return build_spec_html(specs, accent_color)
