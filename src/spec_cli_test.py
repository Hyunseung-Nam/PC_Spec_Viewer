import platform
from datetime import datetime
from typing import Any, Dict, List, Tuple

import psutil
import wmi


def gb(n: int) -> str:
    return f"{n / (1024**3):.2f} GB"


def get_cpu(c: Any) -> str:
    cpus = c.Win32_Processor()
    return cpus[0].Name.strip() if cpus else "N/A"


def get_ram() -> str:
    return gb(psutil.virtual_memory().total)


def get_baseboard(c: Any) -> str:
    bbs = c.Win32_BaseBoard()
    if not bbs:
        return "N/A"
    bb = bbs[0]
    manu = (bb.Manufacturer or "").strip()
    prod = (bb.Product or "").strip()
    return f"{manu} {prod}".strip() or "N/A"


def get_gpus(c: Any) -> List[str]:
    gpus = []
    for g in c.Win32_VideoController():
        name = (g.Name or "").strip()
        if name:
            gpus.append(name)
    return gpus or ["N/A"]


def get_physical_disks_via_storage_namespace() -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    SSD/HDD 분류를 최대한 정확하게:
    root\Microsoft\Windows\Storage 의 MSFT_PhysicalDisk.MediaType 사용
    MediaType (환경에 따라 다를 수 있으나 보통):
      4 = SSD
      3 = HDD
      그 외 = Unknown
    """
    c_storage: Any = wmi.WMI(namespace=r"root\Microsoft\Windows\Storage")

    ssds: List[Dict[str, str]] = []
    hdds: List[Dict[str, str]] = []

    for d in c_storage.MSFT_PhysicalDisk():
        name = (getattr(d, "FriendlyName", None) or getattr(d, "Model", None) or "Unknown").strip()
        size = getattr(d, "Size", None)
        size_str = gb(int(size)) if size is not None else "N/A"
        media = getattr(d, "MediaType", None)

        item = {"name": name, "size": size_str}

        if media == 4:
            ssds.append(item)
        elif media == 3:
            hdds.append(item)
        else:
            # Unknown은 SSD/HDD 둘 다로 안 넣고, 필요하면 따로 표시해도 됨
            pass

    return ssds, hdds


def get_disks_fallback_win32() -> List[Dict[str, str]]:
    """
    Storage namespace가 막히는 환경용 fallback:
    SSD/HDD 구분은 불완전할 수 있음(모델/미디어타입 문자열 의존)
    """
    c: Any = wmi.WMI()
    disks: List[Dict[str, str]] = []
    for d in c.Win32_DiskDrive():
        model = (d.Model or "Unknown").strip()
        size = gb(int(d.Size)) if d.Size is not None else "N/A"
        media = (d.MediaType or "").strip()
        # 아주 거친 추정(환경마다 신뢰도 낮음)
        guess = "SSD" if "ssd" in (model + " " + media).lower() else "HDD/Unknown"
        disks.append({"type": guess, "name": model, "size": size})
    return disks


def main() -> None:
    c: Any = wmi.WMI()

    print("=" * 60)
    print(f"PC SPEC CLI TEST | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    print(f"CPU : {get_cpu(c)}")
    print(f"RAM : {get_ram()}")
    print(f"MB  : {get_baseboard(c)}")
    print("VGA :")
    for g in get_gpus(c):
        print(f"  - {g}")

    # SSD/HDD
    try:
        ssds, hdds = get_physical_disks_via_storage_namespace()
        print("SSD :")
        if ssds:
            for d in ssds:
                print(f"  - {d['name']} ({d['size']})")
        else:
            print("  - N/A")

        print("HDD :")
        if hdds:
            for d in hdds:
                print(f"  - {d['name']} ({d['size']})")
        else:
            print("  - N/A")

    except Exception as e:
        # Storage namespace 접근 실패 시 fallback
        print("SSD/HDD : (fallback)")
        for d in get_disks_fallback_win32():
            print(f"  - {d['type']} | {d['name']} ({d['size']})")

    print("=" * 60)
    print("DONE.")


if __name__ == "__main__":
    main()
