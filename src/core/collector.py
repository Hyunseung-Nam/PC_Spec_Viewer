# 본 소스코드는 내부 사용 및 유지보수 목적에 한해 제공됩니다.
# 무단 재배포 및 상업적 재사용은 허용되지 않습니다.
# core/collector.py

from __future__ import annotations

"""
시스템 사양 수집 모듈
Windows WMI, platform, psutil을 사용하여 CPU/RAM/M/B/VGA/SSD/HDD 정보를 수집

- collect_all_specs()에서 모든 사양을 수집하여 딕셔너리로 반환
- controller.py에서 호출되어 View에 표시될 데이터 제공
- Windows 전용 WMI 사용 (wmi 모듈 필요)
"""
import logging
import platform
import psutil

logger = logging.getLogger(__name__)

try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("wmi 모듈을 사용할 수 없습니다. 일부 정보 수집이 제한될 수 있습니다.")
    
# --- (추가) DXGI 기반 GPU/VRAM 수집 모듈 로드 (실패 시에도 안전) ---
try:
    # core 패키지로 import 되는 경우(정상)
    from .gpu_dxgi import collect_gpu_dxgi_strings, is_dxgi_available
    
except Exception:
    collect_gpu_dxgi_strings = None  # type: ignore
    def is_dxgi_available() -> bool:  # fallback
        return False
    logger.info("DXGI 모듈을 사용할 수 없습니다. GPU VRAM은 WMI 방식으로 폴백됩니다.")

STORAGE_NAMESPACE = r"root\Microsoft\Windows\Storage"
MEDIA_TYPE_SSD = 4
MEDIA_TYPE_HDD = 3
MEDIA_TYPE_UNKNOWN = 0
BUS_TYPE_NVME = 17
BUS_TYPE_NVME_STR = "nvme"
ROTATION_RATE_HDD_THRESHOLD = 1000
BYTES_PER_GB = 1024 ** 3


def _is_windows_wmi_available() -> bool:
    """
    Windows 환경에서 WMI 사용 가능 여부를 반환한다.

    Args:
        없음

    Returns:
        bool: Windows이며 WMI 사용 가능 시 True
    """
    return platform.system() == "Windows" and WMI_AVAILABLE


def _is_portable_system(wmi_conn=None) -> bool:
    """
    휴대형 시스템 여부를 반환한다.

    Args:
        wmi_conn: WMI 연결 객체 (None이면 새로 생성)

    Returns:
        bool: 노트북/태블릿 등 휴대형이면 True
    """
    if not _is_windows_wmi_available():
        return False

    try:
        if wmi_conn is None:
            wmi_conn = wmi.WMI()

        enclosures = wmi_conn.Win32_SystemEnclosure()
        if enclosures:
            chassis_types = enclosures[0].ChassisTypes or []
            portable_types = {8, 9, 10, 14, 30, 31, 32}
            if any(ct in portable_types for ct in chassis_types):
                return True

        systems = wmi_conn.Win32_ComputerSystem()
        if systems:
            pc_system_type = int(getattr(systems[0], "PCSystemType", 0) or 0)
            pc_system_type_ex = int(getattr(systems[0], "PCSystemTypeEx", 0) or 0)
            if pc_system_type in (2, 8) or pc_system_type_ex in (2, 8):
                return True
    except Exception as e:
        logger.warning(f"휴대형 시스템 판별 실패: {e}")

    return False


def _is_replaceable_ram(mem) -> bool:
    """
    교체형 RAM 여부를 반환한다.

    DIMM 등 교체형으로 확정되는 경우만 True로 판단한다.

    Args:
        mem: Win32_PhysicalMemory 객체

    Returns:
        bool: 교체형 RAM이면 True
    """
    form_factor = int(getattr(mem, "FormFactor", 0) or 0)
    device_locator = (getattr(mem, "DeviceLocator", "") or "").upper()
    bank_label = (getattr(mem, "BankLabel", "") or "").upper()
    locator_text = f"{device_locator} {bank_label}"

    if form_factor == 16:
        return False

    if "SOLDER" in locator_text or "ONBOARD" in locator_text or "SYSTEM BOARD" in locator_text:
        return False

    if form_factor == 12 or "SODIMM" in locator_text:
        return False

    if form_factor == 8 or "DIMM" in locator_text:
        return True

    return False


def collect_cpu(wmi_conn=None) -> str:
    """
    CPU 정보 수집
    
    Windows에서는 WMI Win32_Processor를 사용하고
    실패 시 platform.processor()를 fallback으로 사용
    
    Args:
        wmi_conn: WMI 연결 객체 (None이면 새로 생성, 성능 최적화를 위해 재사용 권장)
    
    Returns:
        str: CPU 이름 (예: "Intel(R) Core(TM) i5-14400F @ 2.50GHz")
    """
    try:
        if _is_windows_wmi_available():
            if wmi_conn is None:
                wmi_conn = wmi.WMI()
            processors = wmi_conn.Win32_Processor()
            if processors:
                cpu_name = processors[0].Name.strip()
                return cpu_name
        logger.debug("CPU: WMI 값을 얻지 못해 platform.processor()로 대체")
        return platform.processor() or "정보 없음"
    except Exception as e:
        logger.exception("CPU 정보 수집 실패")
        return "정보 없음"


def collect_ram(wmi_conn=None) -> tuple[str, list[str]] | None:
    """
    RAM 정보 수집
    
    Windows WMI Win32_PhysicalMemory를 사용하여 교체형 메모리 모듈의
    용량, 제조사, 속도 수집
    
    ※ 제조일/생산일 정보는
    제조사별 표준이 없어 정확성을 보장하기 어려워
    기본 제공 항목에서 제외하였습니다.
    
    Args:
        wmi_conn: WMI 연결 객체 (None이면 새로 생성, 성능 최적화를 위해 재사용 권장)
    
    Returns:
        tuple[str, list[str]] | None: {
            성공 + 교체형 있음: ("32GB", ["SAMSUNG 5600MHz 16GB", ...])
            성공 + 교체형 있음 + 모듈 정보 없음: ("32GB", ["모듈 정보 미제공"])
            성공 + 교체형 없음(온보드만): ("32GB", [])
            실패: None
        }
    """
    ram_list : list[str] = []
    total_gb : float = 0.0
    wmi_total_gb : float = 0.0
    replaceable_seen = False
    wmi_attempted = False
    is_portable = False
        
    try:
        if _is_windows_wmi_available():
            wmi_attempted = True
            if wmi_conn is None:
                wmi_conn = wmi.WMI()
            is_portable = _is_portable_system(wmi_conn)
            memory_modules = wmi_conn.Win32_PhysicalMemory() or []
            
            for mem in memory_modules:
                try:
                    size_bytes = int(mem.Capacity or 0)
                    if size_bytes > 0:
                        wmi_total_gb += size_bytes / (1024 ** 3)
                    if is_portable:
                        continue
                    if not _is_replaceable_ram(mem):
                        continue
                    replaceable_seen = True
                    if size_bytes <= 0:
                        continue
                    size_gb = size_bytes / (1024 ** 3)
                    speed = mem.Speed or "알 수 없음"
                    manufacturer = mem.Manufacturer or "알 수 없음"

                    ram_list.append(f"{manufacturer} {speed}MHz {size_gb:.0f}GB")
                    
                    total_gb += size_gb
                    
                except Exception as e:
                    logger.warning(f"RAM 모듈 정보 수집 중 오류: {e}")
                    continue
        total_gb = wmi_total_gb
        if total_gb <= 0:
            return None

        if not wmi_attempted:
            logger.info("RAM: WMI 미사용 → 총 용량만 반환")
            return f"{total_gb:.0f}GB", ["모듈 정보 미제공"]

        if replaceable_seen and not ram_list:
            logger.info("RAM: 교체형 모듈 정보 없음 → 모듈 정보 미제공 표시")
            return f"{total_gb:.0f}GB", ["모듈 정보 미제공"]

        if not replaceable_seen:
            logger.info("RAM: 교체형 모듈 없음 → 총 용량만 반환")
            return f"{total_gb:.0f}GB", []

        return f"{total_gb:.0f}GB", ram_list
    except Exception:
        logger.exception("RAM 수집 전체 실패")
        return None

def collect_baseboard(wmi_conn=None) -> str:
    """
    메인보드 정보 수집
    
    Windows WMI Win32_BaseBoard를 사용하여 제조사, 제품명, 버전을 수집
    버전이 "x.x" 같은 기본값이면 생략
    
    Args:
        wmi_conn: WMI 연결 객체 (None이면 새로 생성, 성능 최적화를 위해 재사용 권장)
    
    Returns:
        str: 메인보드 정보 (예: "Gigabyte B760M AORUS ELITE AX")
    """
    try:
        if _is_windows_wmi_available():
            if wmi_conn is None:
                wmi_conn = wmi.WMI()
            boards = wmi_conn.Win32_BaseBoard()
            if boards:
                manufacturer = boards[0].Manufacturer or ""
                product = boards[0].Product or ""
                version = boards[0].Version or ""
                if version and version.strip() and version.strip() != "x.x":
                    return f"{manufacturer} {product} {version}".strip()
                else:
                    logger.debug("M/B: Version이 기본값(x.x)이라 생략")
                    return f"{manufacturer} {product}".strip()
            else:
                logger.info("M/B: Win32_BaseBoard 결과가 비어있음")
                

    except Exception as e:
        logger.exception("메인보드 정보 수집 실패")
    
    return "정보 없음"


def collect_gpu(wmi_conn=None) -> list[str]:
    """
    GPU 정보 수집

    우선순위:
    1) DXGI(DirectX Graphics Infrastructure) 기반: 전용 VRAM(DedicatedVideoMemory) 조회 (가장 정확)
    2) 실패/미지원 시 WMI(Win32_VideoController) 기반 폴백

    - DXGI: 전용 VRAM이 1GB 미만(iGPU 등)이면 메모리 표기를 생략
    - WMI: AdapterRAM이 음수/0/1GB 미만 등 비정상 값이 있을 수 있어 메모리 표기를 생략

    Args:
        wmi_conn: WMI 연결 객체 (None이면 새로 생성, DXGI 실패 시 WMI fallback에서 사용)

    Returns:
        list[str]: GPU 정보 문자열 리스트
            예: ["NVIDIA GeForce RTX 3050 (6.0GB / NVIDIA)", "Intel UHD Graphics (Intel)"]
    """
    # --- 1) DXGI 우선 ---
    if (
        platform.system() == "Windows"
        and is_dxgi_available()
        and collect_gpu_dxgi_strings is not None
    ):
        try:
            dxgi_list = collect_gpu_dxgi_strings(logger=logger)
            if dxgi_list:
                return dxgi_list
        except Exception:
            # DXGI가 어떤 이유로든 실패하면 WMI로 폴백
            logger.exception("GPU: DXGI 수집 실패. WMI로 폴백합니다.")
    
    # --- 2) WMI fallback ---
    gpu_list: list[str] = []
    try:
        if _is_windows_wmi_available():
            if wmi_conn is None:
                wmi_conn = wmi.WMI()
            gpus = wmi_conn.Win32_VideoController()
            logger.info(f"GPU: Win32_VideoController {len(gpus)}개 감지")
            
            for gpu in gpus:
                try:
                    name = gpu.Name or "알 수 없음"
                    adapter_ram = gpu.AdapterRAM or 0
                    if adapter_ram:
                        if adapter_ram <= 0 or adapter_ram < (1024 ** 3):
                            logger.info(f"GPU: AdapterRAM 비정상 값 | {adapter_ram} | Name={name}")
                            memory_str = ""
                        else:
                            memory_gb = adapter_ram / (1024 ** 3)
                            memory_str = f"{memory_gb:.0f}GB"
                    else:
                        logger.info(f"GPU: AdapterRAM 미제공/0 | Name={name}")
                        memory_str = ""
                    
                    manufacturer = ""
                    if hasattr(gpu, 'AdapterCompatibility') and gpu.AdapterCompatibility:
                        manufacturer = gpu.AdapterCompatibility
                    
                    if memory_str and manufacturer:
                        gpu_str = f"{name} ({memory_str} / {manufacturer})"
                    elif memory_str:
                        gpu_str = f"{name} ({memory_str})"
                    elif manufacturer:
                        gpu_str = f"{name} ({manufacturer})"
                    else:
                        gpu_str = name
                    
                    gpu_list.append(gpu_str)
                except Exception as e:
                    logger.warning(f"GPU 정보 수집 중 오류: {e}")
                    continue
    except Exception as e:
        logger.exception("GPU 정보 수집 실패")
    
    return gpu_list if gpu_list else ["정보 없음"]


def collect_storage(wmi_conn=None, wmi_storage=None) -> tuple[list[str], list[str]]:
    """
    저장장치 정보 수집 및 SSD/HDD 구분

    Windows WMI (root\\Microsoft\\Windows\\Storage)의 MSFT_PhysicalDisk를 사용하여
    MediaType으로 SSD(4)/HDD(3)를 우선 구분
    MediaType이 Unknown(0)/None인 경우, BusType/SeekPenalty/RotationRate로 보조 판단
      - BusType == NVMe  -> SSD
      - SeekPenalty is False -> SSD 가능성 높음
      - RotationRate >= 임계값 -> HDD

    Args:
        wmi_conn: WMI 연결 객체 (사용 안 함, 호환성용)
        wmi_storage: Storage 네임스페이스 WMI 연결 객체 (None이면 새로 생성, 성능 최적화를 위해 재사용 권장)

    Returns:
        tuple[list[str], list[str]]: (ssd_list, hdd_list)
    """
    ssd_list: list[str] = []
    hdd_list: list[str] = []
    unknown_list: list[str] = []

    if not _is_windows_wmi_available():
        return ssd_list, hdd_list

    try:
        if wmi_storage is None:
            wmi_storage = wmi.WMI(namespace=STORAGE_NAMESPACE)

        for disk in wmi_storage.MSFT_PhysicalDisk():
            try:
                name = getattr(disk, "FriendlyName", None) or getattr(disk, "Model", None) or "알 수 없음"
                name = str(name).strip() if name else "알 수 없음"

                size = getattr(disk, "Size", None)
                size_gb = (int(size) / BYTES_PER_GB) if size is not None else 0.0

                storage_str = f"{name} ({size_gb:.2f}GB)"

                media_type = getattr(disk, "MediaType", None)

                if media_type == MEDIA_TYPE_SSD:
                    ssd_list.append(storage_str)
                    logger.info(f"디스크 ({name}): MediaType={MEDIA_TYPE_SSD} → SSD")
                    continue

                if media_type == MEDIA_TYPE_HDD:
                    hdd_list.append(storage_str)
                    logger.info(f"디스크 ({name}): MediaType={MEDIA_TYPE_HDD} → HDD")
                    continue

                if media_type in (MEDIA_TYPE_UNKNOWN, None):
                    bus_type = getattr(disk, "BusType", None)
                    seek_penalty = getattr(disk, "SeekPenalty", None)
                    rotation_rate = getattr(disk, "RotationRate", None)

                    is_ssd: bool | None = None

                    if bus_type == BUS_TYPE_NVME:
                        is_ssd = True
                        logger.info(f"디스크 ({name}): MediaType={media_type}, BusType=NVMe → SSD")

                    if is_ssd is None and seek_penalty is False:
                        is_ssd = True
                        logger.info(f"디스크 ({name}): MediaType={media_type}, SeekPenalty=False → SSD")

                    if is_ssd is None and rotation_rate is not None:
                        try:
                            rotation_rate_int = int(rotation_rate)
                            if rotation_rate_int >= ROTATION_RATE_HDD_THRESHOLD:
                                is_ssd = False
                                logger.info(
                                    f"디스크 ({name}): MediaType={media_type}, RotationRate={rotation_rate_int} → HDD"
                                )
                        except (ValueError, TypeError) as e:
                            logger.debug(
                                f"RotationRate 파싱 실패: {rotation_rate} ({type(rotation_rate)}): {e}"
                            )

                    if is_ssd is True:
                        ssd_list.append(storage_str)
                        continue
                    if is_ssd is False:
                        hdd_list.append(storage_str)
                        continue

                    unknown_list.append(storage_str)
                    logger.debug(
                        f"디스크 분류 불가(표시 제외): {storage_str}"
                        f"MediaType={media_type}, BusType={bus_type}, SeekPenalty={seek_penalty}, RotationRate={rotation_rate}"
                    )
                    continue

                unknown_list.append(storage_str)
                logger.debug(f"디스크 MediaType 비정상(표시 제외): {storage_str} | MediaType={media_type}")

            except Exception as e:
                logger.warning(f"Storage 네임스페이스 디스크 정보 수집 중 오류: {e}")
                continue

    except Exception as e:
        logger.warning("Storage 네임스페이스 접근 실패 (권한/WMI 서비스/OS 상태에 따라 발생할 수 있음)", exc_info=True)
        return ssd_list, hdd_list

    if unknown_list:
        logger.debug(f"분류 불가 디스크 {len(unknown_list)} (표시 제외)개")
        
    if not ssd_list and not hdd_list and unknown_list:
        logger.info("Storage: 디스크 감지됨 but 분류 불가 → 표시 제외(오분류 방지)")
    logger.info(f"Storage: SSD {len(ssd_list)}개 / HDD {len(hdd_list)}개 / Unknown {len(unknown_list)}개(표시 제외)")

    return ssd_list, hdd_list


def collect_all_specs() -> dict:
    """
    모든 시스템 사양을 수집하여 딕셔너리로 반환
    WMI 연결을 재사용하여 성능 최적화 (5번 연결 → 2번 연결)
    
    CPU, RAM, 메인보드, GPU, SSD, HDD 정보를 각각의 collect_*() 함수로 수집
    
    Returns:
        dict: {
            "cpu": str,
            "ram": list[str], str
            "mainboard": str,
            "vga": list[str],
            "ssd": list[str],
            "hdd": list[str]
        }
    """
    logger.info("시스템 사양 수집 시작")
    
    # WMI 연결을 한 번만 생성하여 재사용 (성능 최적화)
    wmi_conn = None
    wmi_storage = None
    
    try:
        if _is_windows_wmi_available():
            wmi_conn = wmi.WMI()
            wmi_storage = wmi.WMI(namespace=STORAGE_NAMESPACE)
    except Exception as e:
        logger.warning("WMI 연결 생성 실패, 각 함수에서 개별 연결 시도: %s", e)
    
    # WMI 연결을 재사용하여 수집
    cpu = collect_cpu(wmi_conn)
    ram = collect_ram(wmi_conn)
    mainboard = collect_baseboard(wmi_conn)
    vga = collect_gpu(wmi_conn)
    ssd, hdd = collect_storage(wmi_conn, wmi_storage)
    
    specs = {
        "cpu": cpu,
        "ram": ram,
        "mainboard": mainboard,
        "vga": vga,
        "ssd": ssd,
        "hdd": hdd
    }
    
    logger.info("시스템 사양 수집 완료")
    
    logger.info(
    "시스템 사양 수집 요약 | "
    f"RAM={len(ram[0])}개, VGA={len(vga)}개, SSD={len(ssd)}개, HDD={len(hdd)}개")
    return specs