"""
시스템 하드웨어 자동 감지 엔진 (Hardware Auto-Detection Engine)
Linux 커널(procfs, sysfs), DMI, NVML, psutil, PipeWire 인터페이스를 통해
어떤 시스템 환경에서도 CPU, GPU, 메인보드, RAM, SSD, 오디오 정보를 지능적으로 자동 인식합니다.
"""

import os
import re
import glob
import subprocess
import psutil
from config import HardwareConfig


class HardwareDetector:
    """
    하드웨어 스펙 자동 감지 및 HardwareConfig 오버라이드 병합기
    """
    @staticmethod
    def get_cpu_info() -> dict:
        # 1. 모델명 추출 (/proc/cpuinfo)
        model_name = "CPU Processor"
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        raw = line.split(":", 1)[1].strip()
                        # '8-Core Processor' 같은 군더더기 제거
                        clean = re.sub(r'\s+\d+-Core\s+Processor', '', raw)
                        clean = re.sub(r'\(R\)|\(TM\)', '', clean).strip()
                        model_name = clean
                        break
        except Exception:
            pass

        # 2. 물리 코어 및 논리 스레드
        physical_cores = psutil.cpu_count(logical=False) or 8
        logical_threads = psutil.cpu_count(logical=True) or 16

        # 3. 최대 부스트 클럭 (MHz)
        max_clock = 5000.0
        try:
            freq = psutil.cpu_freq()
            if freq and freq.max > 0:
                max_clock = float(freq.max)
            else:
                # sysfs cpufreq 검사
                with open("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq", "r") as f:
                    max_clock = float(f.read().strip()) / 1000.0
        except Exception:
            if "9800X3D" in model_name:
                max_clock = 5200.0
            elif "7800X3D" in model_name:
                max_clock = 5050.0

        # 4. L3 캐시 용량 및 라벨
        cache_label = "L3 Cache"
        try:
            l3_path = "/sys/devices/system/cpu/cpu0/cache/index3/size"
            if os.path.exists(l3_path):
                with open(l3_path, "r") as f:
                    raw_size = f.read().strip().upper()
                if "K" in raw_size:
                    kb = int(raw_size.replace("K", ""))
                    mb = kb // 1024
                elif "M" in raw_size:
                    mb = int(raw_size.replace("M", ""))
                else:
                    mb = 32

                if mb >= 96 or "X3D" in model_name:
                    cache_label = f"3D V-Cache ({mb}MB L3)"
                else:
                    cache_label = f"L3 Cache ({mb}MB)"
        except Exception:
            if "X3D" in model_name:
                cache_label = "3D V-Cache (96MB L3)"
            else:
                cache_label = "L3 Cache (32MB)"

        # TDP 추정
        tdp_w = 140.0
        if "X3D" in model_name or "9800" in model_name:
            tdp_w = 140.0
        elif "14900" in model_name or "13900" in model_name:
            tdp_w = 253.0

        # HardwareConfig 오버라이드 우선 적용
        final_model = HardwareConfig.CPU_MODEL or model_name
        final_max_clock = HardwareConfig.CPU_MAX_CLOCK_MHZ or max_clock
        final_tdp = HardwareConfig.CPU_TDP_W or tdp_w
        final_cache_label = HardwareConfig.CPU_CACHE_LABEL or cache_label

        return {
            "model": final_model,
            "physical_cores": physical_cores,
            "logical_threads": logical_threads,
            "max_clock_mhz": final_max_clock,
            "tdp_w": final_tdp,
            "cache_label": final_cache_label
        }

    @staticmethod
    def get_motherboard_info() -> dict:
        vendor = "Mainboard"
        board = "Motherboard"
        bios = "BIOS"

        try:
            with open("/sys/class/dmi/id/board_vendor", "r") as f:
                vendor = f.read().strip()
            with open("/sys/class/dmi/id/board_name", "r") as f:
                board = f.read().strip()
            with open("/sys/class/dmi/id/bios_version", "r") as f:
                bios = f.read().strip()
        except Exception:
            pass

        # 칩셋 식별
        chipset = "System Chipset"
        for candidate in ["B850", "X870", "B650", "X670", "A620", "B550", "X570",
                          "Z790", "B760", "Z890", "B860", "Z690", "B660"]:
            if candidate in board.upper():
                chipset = f"AMD {candidate}" if candidate.startswith(("B8", "X8", "B6", "X6", "A6", "B5", "X5")) else f"Intel {candidate}"
                break

        full_name = f"{vendor} {board}".replace("Gigabyte Technology Co., Ltd.", "GIGABYTE").strip()
        sub_text = f"BIOS: {bios}  |  PCIe Link Active  |  {chipset}"

        # HardwareConfig 오버라이드
        final_name = HardwareConfig.MOBO_NAME or full_name
        final_sub = HardwareConfig.MOBO_SUB or sub_text

        return {
            "vendor": vendor,
            "board_name": board,
            "full_name": final_name,
            "bios_ver": bios,
            "chipset": chipset,
            "sub_text": final_sub
        }

    @staticmethod
    def get_gpu_info(detected_name: str = "NVIDIA GPU", power_limit_w: float = 300.0, vram_total_mb: float = 16384.0) -> dict:
        # 모델명 정제
        clean_name = detected_name
        if "NVIDIA" in clean_name and "GeForce" in clean_name:
            clean_name = clean_name.replace("NVIDIA GeForce ", "")
        
        # VRAM 용량 라벨
        vram_gb = int(round(vram_total_mb / 1024.0)) if vram_total_mb > 0 else 16
        is_blackwell = any(k in clean_name for k in ["5090", "5080", "5070"])
        vram_type = "GDDR7" if is_blackwell else "GDDR6X"
        default_vram_label = f"VRAM ({vram_type} {vram_gb}GB)"

        # 최대 클럭
        max_clock = 2600.0
        if "5070" in clean_name or "4070" in clean_name:
            max_clock = 2650.0
        elif "5080" in clean_name or "4080" in clean_name:
            max_clock = 2750.0
        elif "5090" in clean_name or "4090" in clean_name:
            max_clock = 2800.0

        final_model = HardwareConfig.GPU_MODEL or clean_name
        final_vram_label = HardwareConfig.GPU_VRAM_LABEL or default_vram_label
        final_max_clock = HardwareConfig.GPU_MAX_CLOCK_MHZ or max_clock
        final_tgp = HardwareConfig.GPU_TGP_W or power_limit_w

        return {
            "model": final_model,
            "vram_label": final_vram_label,
            "max_clock_mhz": final_max_clock,
            "tgp_w": final_tgp
        }

    @staticmethod
    def get_ram_info() -> dict:
        vm = psutil.virtual_memory()
        total_gb = int(round(vm.total / (1024**3)))
        
        default_model = "DDR5 High-Speed Memory"
        default_spec = f"Dual-Channel  |  Total {total_gb}GB  |  High Speed"

        if HardwareConfig.RAM_MODEL:
            final_model = f"{HardwareConfig.RAM_MODEL} (DDR5 {total_gb}GB)"
        else:
            final_model = f"DDR5 System Memory ({total_gb}GB)"

        final_spec = HardwareConfig.RAM_SPEC or default_spec

        return {
            "model": final_model,
            "spec": final_spec,
            "total_gb": total_gb
        }

    @staticmethod
    def get_ssd_info() -> dict:
        model = "NVMe PCIe SSD"
        try:
            for p in glob.glob("/sys/block/nvme*/device/model"):
                with open(p, "r") as f:
                    raw = f.read().strip()
                if "Samsung" in raw or "WD" in raw or "Crucial" in raw or "SK" in raw or "Kingston" in raw:
                    # 'Samsung SSD 980 PRO 1TB' -> 'Samsung 980 Pro'
                    clean = raw.replace("SSD ", "").replace(" 1TB", "").replace(" 2TB", "").replace(" 500GB", "").strip()
                    model = f"{clean} (PCIe NVMe)"
                    break
        except Exception:
            pass

        final_model = HardwareConfig.SSD_MODEL or model
        final_spec = HardwareConfig.SSD_SPEC or "PCIe Gen4 x4  |  High-Speed NVMe"

        return {
            "model": final_model,
            "spec": final_spec
        }

    @staticmethod
    def get_audio_info() -> dict:
        device_name = "Master Audio Speakers"
        try:
            res = subprocess.run(
                ["wpctl", "inspect", "@DEFAULT_AUDIO_SINK@"],
                capture_output=True, text=True, timeout=0.15
            )
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if "node.description" in line:
                        device_name = line.split("=", 1)[1].strip().strip('"')
                        break
        except Exception:
            pass

        final_device = HardwareConfig.AUDIO_DEVICE or device_name
        final_title = HardwareConfig.AUDIO_ENGINE or "PipeWire Master Audio"

        return {
            "title": final_title,
            "device": final_device
        }

    @staticmethod
    def get_router_info() -> str:
        return HardwareConfig.ROUTER_MODEL or "Gigabit Gaming Router"
