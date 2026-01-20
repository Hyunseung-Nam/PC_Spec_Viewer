# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
"""
DXGI를 통해 GPU 어댑터 정보를 수집한다.
Windows 환경에서 GPU 문자열을 안정적으로 얻기 위해 존재한다.

- collector.py에서 DXGI 기반 GPU 수집 시 사용
- Windows 전용(DXGI/COM) 환경에서만 동작
"""
# core/gpu_dxgi.py

from __future__ import annotations

import platform
import ctypes
from ctypes import wintypes
from dataclasses import dataclass

# ------------------------------------------------------------
# Public API
# ------------------------------------------------------------

HRESULT = ctypes.c_long

def is_dxgi_available() -> bool:
    """
    DXGI 사용 가능 여부를 반환한다.

    import 단계에서 DLL 로드를 강제하지 않도록 런타임에 확인한다.

    Args:
        없음

    Returns:
        bool: dxgi.dll 로드 가능 여부
    """
    if platform.system() != "Windows":
        return False
    try:
        ctypes.WinDLL("dxgi")
        return True
    except Exception:
        return False


@dataclass(frozen=True)
class DxgiGpu:
    """
    DXGI로 수집한 GPU 어댑터 정보를 담는다.

    - 책임: 어댑터 메타데이터 보관
    - 비책임: 수집/포맷팅 로직
    - 사용처: collect_gpu_dxgi_raw 반환 타입
    """
    name: str
    vendor: str
    dedicated_vram_bytes: int  # DedicatedVideoMemory
    shared_sys_bytes: int      # SharedSystemMemory


def collect_gpu_dxgi_raw(logger=None) -> list[DxgiGpu]:
    """
    DXGI로 GPU 어댑터 정보를 수집해 리스트로 반환한다.

    DLL 로드 및 COM 호출은 이 함수 내부에서만 수행한다.

    Args:
        logger: 로깅용 객체(옵션)

    Returns:
        list[DxgiGpu]: 수집된 GPU 목록
    """
    if platform.system() != "Windows":
        return []

    # 1) dxgi.dll 로드
    try:
        dxgi = ctypes.WinDLL("dxgi", use_last_error=True)
    except Exception as e:
        if logger:
            logger.info(f"GPU(DXGI): dxgi.dll 로드 실패: {e!r}")
        return []

    # 2) ole32.dll 로드 및 CLSIDFromString 준비
    try:
        ole32 = ctypes.WinDLL("ole32", use_last_error=True)
        ole32.CLSIDFromString.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(GUID)]
        ole32.CLSIDFromString.restype = HRESULT
    except Exception as e:
        if logger:
            logger.info(f"GPU(DXGI): ole32.dll/CLSIDFromString 준비 실패: {e!r}")
        return []

    def guid_from_string(s: str) -> GUID:
        """
        문자열 CLSID를 GUID 구조체로 변환한다.

        Args:
            s: GUID 문자열

        Returns:
            GUID: 변환된 GUID
        """
        g = GUID()
        hr = ole32.CLSIDFromString(s, ctypes.byref(g))
        if hr != 0:
            raise OSError(f"CLSIDFromString failed hr=0x{hr & 0xFFFFFFFF:08X} for {s}")
        return g

    # 3) CreateDXGIFactory 시그니처 설정
    try:
        dxgi.CreateDXGIFactory.argtypes = [ctypes.POINTER(GUID), ctypes.POINTER(ctypes.c_void_p)]
        dxgi.CreateDXGIFactory.restype = HRESULT
    except Exception as e:
        if logger:
            logger.info(f"GPU(DXGI): CreateDXGIFactory 시그니처 설정 실패: {e!r}")
        return []

    # 4) Factory 생성
    IID_IDXGIFactory = guid_from_string("{7b7166ec-21c7-44ae-b21a-c9ae321ae369}")
    factory_ptr = ctypes.c_void_p()
    hr = dxgi.CreateDXGIFactory(ctypes.byref(IID_IDXGIFactory), ctypes.byref(factory_ptr))
    if _hr_failed(hr) or not factory_ptr.value:
        if logger:
            logger.info(f"GPU(DXGI): CreateDXGIFactory 실패 hr=0x{hr & 0xFFFFFFFF:08X}")
        return []

    factory = ctypes.cast(factory_ptr, ctypes.POINTER(IDXGIFactory))

    enum_adapters = ctypes.WINFUNCTYPE(
        HRESULT,
        ctypes.c_void_p,                 # this
        wintypes.UINT,                   # index
        ctypes.POINTER(ctypes.c_void_p)  # ppAdapter
    )(factory.contents.lpVtbl.contents.EnumAdapters)

    gpus: list[DxgiGpu] = []
    i = 0

    try:
        while True:
            adapter_ptr = ctypes.c_void_p()
            hr_enum = enum_adapters(ctypes.cast(factory, ctypes.c_void_p), i, ctypes.byref(adapter_ptr))

            # HRESULT 비교는 unsigned로도 확인
            hr_enum_u32 = hr_enum & 0xFFFFFFFF
            if hr_enum_u32 == DXGI_ERROR_NOT_FOUND:
                break
            if _hr_failed(hr_enum) or not adapter_ptr.value:
                if logger:
                    logger.info(f"GPU(DXGI): EnumAdapters 실패 idx={i} hr=0x{hr_enum_u32:08X}")
                break

            adapter = ctypes.cast(adapter_ptr, ctypes.POINTER(IDXGIAdapter))

            get_desc = ctypes.WINFUNCTYPE(
                HRESULT,
                ctypes.c_void_p,  # this
                ctypes.POINTER(DXGI_ADAPTER_DESC)
            )(adapter.contents.lpVtbl.contents.GetDesc)

            desc = DXGI_ADAPTER_DESC()
            hr_desc = get_desc(ctypes.cast(adapter, ctypes.c_void_p), ctypes.byref(desc))

            if not _hr_failed(hr_desc):
                name = (desc.Description or "").strip() or "알 수 없음"
                vendor = _vendor_name(int(desc.VendorId))
                dedicated = int(desc.DedicatedVideoMemory)
                shared = int(desc.SharedSystemMemory)

                gpus.append(DxgiGpu(
                    name=name,
                    vendor=vendor,
                    dedicated_vram_bytes=dedicated,
                    shared_sys_bytes=shared
                ))
            else:
                if logger:
                    logger.info(f"GPU(DXGI): GetDesc 실패 idx={i} hr=0x{hr_desc & 0xFFFFFFFF:08X}")

            _com_release(adapter)
            i += 1

    finally:
        _com_release(factory)

    if logger:
        logger.info(f"GPU(DXGI): 어댑터 {len(gpus)}개 감지")

    return gpus


def collect_gpu_dxgi_strings(
    logger=None,
    min_vram_bytes: int = 1024 ** 3,
    sort_by_vram_desc: bool = True,
) -> list[str]:
    """
    DXGI 기반 GPU 표시 문자열을 반환한다.

    VRAM 기준 필터링 및 정렬 정책을 적용한다.

    Args:
        logger: 로깅용 객체(옵션)
        min_vram_bytes: VRAM 표기 최소 기준
        sort_by_vram_desc: 전용 VRAM 내림차순 정렬 여부

    Returns:
        list[str]: GPU 표시 문자열 목록
    """
    gpus = collect_gpu_dxgi_raw(logger=logger)
    if not gpus:
        return []
    
    # 🔴 1) Microsoft 가상 GPU 제거 (핵심)
    gpus = [
        g for g in gpus
        if g.vendor.lower() != "microsoft"
        and "microsoft" not in g.name.lower()
    ]

    if not gpus:
        return []

    if sort_by_vram_desc:
        gpus = sorted(gpus, key=lambda x: x.dedicated_vram_bytes, reverse=True)

    out: list[str] = []
    for g in gpus:
        if g.dedicated_vram_bytes >= min_vram_bytes:
            out.append(f"{g.name} ({_bytes_to_gb_str(g.dedicated_vram_bytes)} / {g.vendor})")
        else:
            out.append(f"{g.name} ({g.vendor})" if g.vendor else g.name)

    return out


# ------------------------------------------------------------
# Internal DXGI COM definitions (import-safe: no DLL load here)
# ------------------------------------------------------------

class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]


class IUnknownVTable(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", ctypes.c_void_p),
        ("AddRef", ctypes.c_void_p),
        ("Release", ctypes.c_void_p),
    ]


class IUnknown(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IUnknownVTable))]


def _com_release(ptr) -> None:
    """
    COM 객체 Release를 안전하게 호출한다.

    Args:
        ptr: COM 객체 포인터

    Returns:
        None
    """
    if not ptr:
        return
    try:
        release_fn = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)(
            ptr.contents.lpVtbl.contents.Release
        )
        release_fn(ctypes.cast(ptr, ctypes.c_void_p))
    except Exception:
        pass


class IDXGIAdapterVTable(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", ctypes.c_void_p),
        ("AddRef", ctypes.c_void_p),
        ("Release", ctypes.c_void_p),
        # IDXGIObject
        ("SetPrivateData", ctypes.c_void_p),
        ("SetPrivateDataInterface", ctypes.c_void_p),
        ("GetPrivateData", ctypes.c_void_p),
        ("GetParent", ctypes.c_void_p),
        # IDXGIAdapter
        ("EnumOutputs", ctypes.c_void_p),
        ("GetDesc", ctypes.c_void_p),
        ("CheckInterfaceSupport", ctypes.c_void_p),
    ]


class IDXGIAdapter(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IDXGIAdapterVTable))]


class IDXGIFactoryVTable(ctypes.Structure):
    _fields_ = [
        ("QueryInterface", ctypes.c_void_p),
        ("AddRef", ctypes.c_void_p),
        ("Release", ctypes.c_void_p),
        # IDXGIObject
        ("SetPrivateData", ctypes.c_void_p),
        ("SetPrivateDataInterface", ctypes.c_void_p),
        ("GetPrivateData", ctypes.c_void_p),
        ("GetParent", ctypes.c_void_p),
        # IDXGIFactory
        ("EnumAdapters", ctypes.c_void_p),
        ("MakeWindowAssociation", ctypes.c_void_p),
        ("GetWindowAssociation", ctypes.c_void_p),
        ("CreateSwapChain", ctypes.c_void_p),
        ("CreateSoftwareAdapter", ctypes.c_void_p),
    ]


class IDXGIFactory(ctypes.Structure):
    _fields_ = [("lpVtbl", ctypes.POINTER(IDXGIFactoryVTable))]


class LUID(ctypes.Structure):
    _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]


class DXGI_ADAPTER_DESC(ctypes.Structure):
    _fields_ = [
        ("Description", wintypes.WCHAR * 128),
        ("VendorId", wintypes.UINT),
        ("DeviceId", wintypes.UINT),
        ("SubSysId", wintypes.UINT),
        ("Revision", wintypes.UINT),
        ("DedicatedVideoMemory", ctypes.c_size_t),
        ("DedicatedSystemMemory", ctypes.c_size_t),
        ("SharedSystemMemory", ctypes.c_size_t),
        ("AdapterLuid", LUID),
    ]


DXGI_ERROR_NOT_FOUND = 0x887A0002  # unsigned


_VENDOR_MAP = {
    0x10DE: "NVIDIA",
    0x1002: "AMD",
    0x1022: "AMD",
    0x8086: "Intel",
    0x1414: "Microsoft",
}


def _vendor_name(vendor_id: int) -> str:
    """
    벤더 ID를 표시용 이름으로 변환한다.

    Args:
        vendor_id: PCI 벤더 ID

    Returns:
        str: 벤더 표시 문자열
    """
    return _VENDOR_MAP.get(vendor_id, f"VEN_{vendor_id:04X}")


def _bytes_to_gb_str(b: int) -> str:
    """
    바이트 값을 GB 문자열로 변환한다.

    Args:
        b: 바이트 값

    Returns:
        str: GB 표기 문자열
    """
    return f"{(b / (1024 ** 3)):.0f}GB"


def _hr_failed(hr: int) -> bool:
    """
    HRESULT 실패 여부를 판정한다.

    Args:
        hr: HRESULT 값

    Returns:
        bool: 실패 여부
    """
    return hr < 0
