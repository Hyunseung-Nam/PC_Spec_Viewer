# core/collector.py

from __future__ import annotations
import logging
import platform
import psutil

logger = logging.getLogger(__name__)

# Windows에서만 wmi 사용
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False
    logger.warning("wmi 모듈을 사용할 수 없습니다. 일부 정보 수집이 제한될 수 있습니다.")


def collect_cpu() -> str:
    """CPU 정보를 수집합니다."""
    try:
        if platform.system() == "Windows" and WMI_AVAILABLE:
            c = wmi.WMI()
            processors = c.Win32_Processor()
            if processors:
                cpu_name = processors[0].Name.strip()
                return cpu_name
        # 대체 방법: platform 사용
        return platform.processor() or "정보 없음"
    except Exception as e:
        logger.exception("CPU 정보 수집 실패")
        return "정보 없음"


def collect_ram() -> list[str]:
    """RAM 정보를 수집합니다. 여러 개의 RAM 모듈 정보를 반환합니다."""
    ram_list = []
    try:
        if platform.system() == "Windows" and WMI_AVAILABLE:
            c = wmi.WMI()
            memory_modules = c.Win32_PhysicalMemory()
            
            for mem in memory_modules:
                try:
                    size_bytes = int(mem.Capacity or 0)
                    size_gb = size_bytes / (1024 ** 3)
                    speed = mem.Speed or "알 수 없음"
                    manufacturer = mem.Manufacturer or "알 수 없음"
                    
                    # 날짜 정보 (있는 경우)
                    date_info = ""
                    if hasattr(mem, 'PartNumber') and mem.PartNumber:
                        # PartNumber에서 날짜 정보 추출 시도
                        pass
                    
                    # 포맷팅: "크기 GB 제조사 속도 날짜"
                    ram_str = f"{size_gb:.2f} GB {manufacturer} {speed}MHz"
                    if date_info:
                        ram_str += f" ({date_info})"
                    
                    ram_list.append(ram_str)
                except Exception as e:
                    logger.warning(f"RAM 모듈 정보 수집 중 오류: {e}")
                    continue
        
        # RAM 정보가 없으면 전체 메모리 정보라도 반환
        if not ram_list:
            total_memory = psutil.virtual_memory().total
            total_gb = total_memory / (1024 ** 3)
            ram_list.append(f"{total_gb:.2f} GB (전체 메모리)")
            
    except Exception as e:
        logger.exception("RAM 정보 수집 실패")
        # 최소한 전체 메모리라도 반환
        try:
            total_memory = psutil.virtual_memory().total
            total_gb = total_memory / (1024 ** 3)
            ram_list.append(f"{total_gb:.2f} GB (전체 메모리)")
        except:
            ram_list.append("정보 없음")
    
    return ram_list if ram_list else ["정보 없음"]


def collect_baseboard() -> str:
    """메인보드 정보를 수집합니다."""
    try:
        if platform.system() == "Windows" and WMI_AVAILABLE:
            c = wmi.WMI()
            boards = c.Win32_BaseBoard()
            if boards:
                manufacturer = boards[0].Manufacturer or ""
                product = boards[0].Product or ""
                version = boards[0].Version or ""
                
                # 버전이 "x.x" 같은 기본값이면 생략
                if version and version.strip() and version.strip() != "x.x":
                    return f"{manufacturer} {product} {version}".strip()
                else:
                    return f"{manufacturer} {product}".strip()
    except Exception as e:
        logger.exception("메인보드 정보 수집 실패")
    
    return "정보 없음"


def collect_gpu() -> list[str]:
    """GPU 정보를 수집합니다. 여러 개의 GPU 정보를 반환합니다."""
    gpu_list = []
    try:
        if platform.system() == "Windows" and WMI_AVAILABLE:
            c = wmi.WMI()
            gpus = c.Win32_VideoController()
            
            for gpu in gpus:
                try:
                    name = gpu.Name or "알 수 없음"
                    adapter_ram = gpu.AdapterRAM or 0
                    
                    # 메모리 크기 포맷팅
                    if adapter_ram:
                        memory_gb = adapter_ram / (1024 ** 3)
                        memory_str = f"{memory_gb:.0f}G"
                    else:
                        memory_str = ""
                    
                    # 제조사 정보
                    manufacturer = ""
                    if hasattr(gpu, 'AdapterCompatibility') and gpu.AdapterCompatibility:
                        manufacturer = gpu.AdapterCompatibility
                    
                    # 포맷팅: "이름 (메모리 / 제조사)"
                    if memory_str and manufacturer:
                        gpu_str = f"{name} ({memory_str} / {manufacturer})"
                    elif memory_str:
                        gpu_str = f"{name} ({memory_str})"
                    else:
                        gpu_str = name
                    
                    gpu_list.append(gpu_str)
                except Exception as e:
                    logger.warning(f"GPU 정보 수집 중 오류: {e}")
                    continue
    except Exception as e:
        logger.exception("GPU 정보 수집 실패")
    
    return gpu_list if gpu_list else ["정보 없음"]


def collect_storage() -> tuple[list[str], list[str]]:
    """
    저장장치 정보를 수집합니다.
    root\Microsoft\Windows\Storage 네임스페이스의 MSFT_PhysicalDisk를 사용하여
    정확하게 SSD/HDD를 구분합니다.
    MediaType: 4 = SSD, 3 = HDD
    
    반환: (ssd_list, hdd_list)
    """
    ssd_list = []
    hdd_list = []
    
    try:
        if platform.system() == "Windows" and WMI_AVAILABLE:
            # 1순위: Storage 네임스페이스 사용 (가장 정확)
            try:
                c_storage = wmi.WMI(namespace=r"root\Microsoft\Windows\Storage")
                
                for disk in c_storage.MSFT_PhysicalDisk():
                    try:
                        # FriendlyName 또는 Model 가져오기
                        name = getattr(disk, "FriendlyName", None) or getattr(disk, "Model", None) or "알 수 없음"
                        name = str(name).strip() if name else "알 수 없음"
                        
                        # Size 가져오기
                        size = getattr(disk, "Size", None)
                        if size is not None:
                            size_bytes = int(size)
                            size_gb = size_bytes / (1024 ** 3)
                        else:
                            size_gb = 0.0
                        
                        # MediaType 확인 (4 = SSD, 3 = HDD)
                        media_type = getattr(disk, "MediaType", None)
                        
                        # BusType, SeekPenalty, RotationRate 확인
                        bus_type = getattr(disk, "BusType", None)
                        seek_penalty = getattr(disk, "SeekPenalty", None)
                        rotation_rate = getattr(disk, "RotationRate", None)
                        
                        storage_str = f"{name} ({size_gb:.2f} GB)"
                        is_ssd = None
                        
                        # 1순위: MediaType == 4 → SSD
                        if media_type == 4:
                            is_ssd = True
                            logger.info(f"디스크 ({name}): MediaType=4 → SSD")
                        # 2순위: MediaType == 3 → HDD
                        elif media_type == 3:
                            is_ssd = False
                            logger.info(f"디스크 ({name}): MediaType=3 → HDD")
                        # 3순위: MediaType == 0 또는 Unknown인 경우 추가 판단
                        elif media_type == 0 or media_type is None:
                            # BusType == NVMe → SSD
                            if bus_type is not None:
                                bus_type_str = str(bus_type).lower()
                                if "nvme" in bus_type_str or bus_type == 17:  # 17 = NVMe
                                    is_ssd = True
                                    logger.info(f"디스크 ({name}): MediaType={media_type}, BusType=NVMe → SSD")
                            
                            # SeekPenalty == False → SSD 가능성 매우 높음
                            if is_ssd is None and seek_penalty is not None:
                                if seek_penalty == False:
                                    is_ssd = True
                                    logger.info(f"디스크 ({name}): MediaType={media_type}, SeekPenalty=False → SSD")
                            
                            # RotationRate >= 1000 → HDD
                            if is_ssd is None and rotation_rate is not None:
                                try:
                                    rotation_rate_int = int(rotation_rate)
                                    if rotation_rate_int >= 1000:
                                        is_ssd = False
                                        logger.info(f"디스크 ({name}): MediaType={media_type}, RotationRate={rotation_rate_int} → HDD")
                                except (ValueError, TypeError):
                                    pass
                            
                            # 그 외 → Unknown (무시)
                            if is_ssd is None:
                                logger.debug(f"디스크 ({name}): MediaType={media_type}, BusType={bus_type}, SeekPenalty={seek_penalty}, RotationRate={rotation_rate} → Unknown (무시)")
                                continue
                        else:
                            # MediaType이 0, 3, 4가 아닌 다른 값인 경우 Unknown
                            logger.debug(f"디스크 ({name}): MediaType={media_type} → Unknown (무시)")
                            continue
                        
                        # 최종 분류
                        if is_ssd:
                            ssd_list.append(storage_str)
                        else:
                            hdd_list.append(storage_str)
                            
                    except Exception as e:
                        logger.warning(f"Storage 네임스페이스 디스크 정보 수집 중 오류: {e}")
                        continue
                
                # Storage 네임스페이스로 성공적으로 수집했으면 반환
                if ssd_list or hdd_list:
                    return ssd_list, hdd_list
                    
            except Exception as e:
                logger.warning(f"Storage 네임스페이스 접근 실패, fallback 사용: {e}")
            
            # 2순위: Fallback - Win32_DiskDrive 사용
            c = wmi.WMI()
            physical_disks = c.Win32_DiskDrive()
            
            for disk in physical_disks:
                try:
                    model = disk.Model or "알 수 없음"
                    size_bytes = int(disk.Size or 0)
                    size_gb = size_bytes / (1024 ** 3)
                    model_lower = model.lower()
                    
                    # Model 이름으로 추정 (불완전하지만 fallback)
                    is_ssd = False
                    if "ssd" in model_lower or "nvme" in model_lower or "m.2" in model_lower or "m2" in model_lower:
                        is_ssd = True
                        logger.info(f"디스크 ({model}): Model 이름으로 SSD 추정 (fallback)")
                    elif "hdd" in model_lower or "hard disk" in model_lower:
                        is_ssd = False
                        logger.info(f"디스크 ({model}): Model 이름으로 HDD 추정 (fallback)")
                    else:
                        # 기본값: HDD로 간주
                        is_ssd = False
                        logger.info(f"디스크 ({model}): 기본값으로 HDD 추정 (fallback)")
                    
                    storage_str = f"{model} ({size_gb:.2f} GB)"
                    
                    if is_ssd:
                        ssd_list.append(storage_str)
                    else:
                        hdd_list.append(storage_str)
                        
                except Exception as e:
                    logger.warning(f"Fallback 디스크 정보 수집 중 오류: {e}")
                    continue
                    
    except Exception as e:
        logger.exception("저장장치 정보 수집 실패")
    
    # 정보가 없으면 빈 리스트 반환 (formatter에서 "정보 없음" 처리)
    return ssd_list, hdd_list


def collect_all_specs() -> dict:
    """
    모든 시스템 사양을 수집하여 딕셔너리로 반환합니다.
    
    반환 형식:
    {
        "cpu": str,
        "ram": list[str],
        "mainboard": str,
        "vga": list[str],
        "ssd": list[str],
        "hdd": list[str]
    }
    """
    logger.info("시스템 사양 수집 시작")
    
    cpu = collect_cpu()
    ram = collect_ram()
    mainboard = collect_baseboard()
    vga = collect_gpu()
    ssd, hdd = collect_storage()
    
    specs = {
        "cpu": cpu,
        "ram": ram,
        "mainboard": mainboard,
        "vga": vga,
        "ssd": ssd,
        "hdd": hdd
    }
    
    logger.info("시스템 사양 수집 완료")
    return specs
