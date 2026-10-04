"""
실시간 고성능 하드웨어 센서 데이터 수집기
NVML(NVIDIA C 바인딩), psutil, PipeWire/wpctl, DMI 커널 인터페이스를 통해 최소 오버헤드로 백그라운드 수집
"""

import time
import os
import subprocess
import socket
import psutil
from PyQt6.QtCore import QThread, pyqtSignal

# NVML (NVIDIA Management Library) import
try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False


class SystemMonitorCollector(QThread):
    """
    백그라운드에서 주기적으로 센서 데이터를 수집하여 UI 스레드로 안전하게 전송
    """
    data_ready = pyqtSignal(dict)

    def __init__(self, interval_ms=800, parent=None):
        super().__init__(parent)
        self.interval_sec = interval_ms / 1000.0
        self.running = True
        
        # NVML 초기화
        self.nvml_initialized = False
        self.gpu_handle = None
        self.gpu_name = "NVIDIA GPU"
        self._init_nvml()

        # I/O 계산용 이전 상태 기록
        self.last_time = time.time()
        self.last_net_io = psutil.net_io_counters()
        self.last_disk_io = psutil.disk_io_counters()

        # CPU 초기화
        psutil.cpu_percent(percpu=True)

        # 메인보드 고정 정보 1회 캐싱
        self.cached_mobo = self._init_motherboard_info()
        self.cached_net_iface = self._init_network_iface()

    def _init_nvml(self):
        if not HAS_NVML:
            return
        try:
            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            if count > 0:
                self.gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                name_raw = pynvml.nvmlDeviceGetName(self.gpu_handle)
                self.gpu_name = name_raw.decode('utf-8') if isinstance(name_raw, bytes) else str(name_raw)
                self.nvml_initialized = True
        except Exception as e:
            print(f"[Collector] NVML Init warning: {e}")
            self.nvml_initialized = False

    def _init_motherboard_info(self):
        vendor = "Gigabyte Technology Co., Ltd."
        board = "B850I AORUS PRO"
        bios = "F13c"
        try:
            with open("/sys/class/dmi/id/board_vendor", "r") as f:
                vendor = f.read().strip()
            with open("/sys/class/dmi/id/board_name", "r") as f:
                board = f.read().strip()
            with open("/sys/class/dmi/id/bios_version", "r") as f:
                bios = f.read().strip()
        except Exception:
            pass
        return {
            "vendor": vendor,
            "board_name": board,
            "bios_ver": bios,
            "chipset": "AMD B850"
        }

    def _init_network_iface(self):
        iface = "eth0"
        ip_addr = "127.0.0.1"
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("1.1.1.1", 80))
            ip_addr = s.getsockname()[0]
            s.close()
            for nic, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.address == ip_addr:
                        iface = nic
                        break
        except Exception:
            iface = "wlp8s0"
            ip_addr = "192.168.50.206"
        return {"iface": iface, "ip": ip_addr}

    def run(self):
        while self.running:
            start_loop = time.time()
            data = self._collect_all()
            self.data_ready.emit(data)

            elapsed = time.time() - start_loop
            sleep_time = max(0.05, self.interval_sec - elapsed)
            time.sleep(sleep_time)

    def stop(self):
        self.running = False
        self.wait(2000)
        if self.nvml_initialized:
            try:
                pynvml.nvmlShutdown()
            except Exception:
                pass

    def _collect_all(self):
        now = time.time()
        dt = max(0.001, now - self.last_time)
        self.last_time = now

        data = {
            "timestamp": now,
            "cpu": self._collect_cpu(),
            "gpu": self._collect_gpu(),
            "memory": self._collect_memory(),
            "disk": self._collect_disk(dt),
            "network": self._collect_network(dt),
            "motherboard": self._collect_motherboard(),
            "audio": self._collect_audio(),
            "processes": self._collect_top_processes(),
            "system": self._collect_system_meta()
        }
        return data

    def _collect_cpu(self):
        per_cpu_percent = psutil.cpu_percent(percpu=True)
        total_percent = psutil.cpu_percent() if per_cpu_percent else 0.0
        
        freqs = psutil.cpu_freq(percpu=True)
        per_cpu_freq = [int(f.current) for f in freqs] if freqs else [0] * len(per_cpu_percent)

        temp_c = 0.0
        try:
            temps = psutil.sensors_temperatures()
            if 'k10temp' in temps:
                for entry in temps['k10temp']:
                    if entry.label == 'Tctl':
                        temp_c = entry.current
                        break
                if temp_c == 0.0 and len(temps['k10temp']) > 0:
                    temp_c = temps['k10temp'][0].current
            elif 'coretemp' in temps and len(temps['coretemp']) > 0:
                temp_c = temps['coretemp'][0].current
        except Exception:
            pass

        fan_rpm = 0
        try:
            fans = psutil.sensors_fans()
            if 'it8686' in fans and len(fans['it8686']) > 0:
                fan_rpm = fans['it8686'][0].current
        except Exception:
            pass

        return {
            "model": "AMD Ryzen 7 9800X3D",
            "cores": 8,
            "threads": 16,
            "total_percent": total_percent,
            "threads_percent": per_cpu_percent,
            "threads_freq": per_cpu_freq,
            "temp_c": temp_c,
            "fan_rpm": fan_rpm
        }

    def _collect_gpu(self):
        if not self.nvml_initialized or not self.gpu_handle:
            return {
                "model": "NVIDIA GeForce RTX 5070 Ti",
                "util_percent": 0,
                "temp_c": 0,
                "power_w": 0.0,
                "power_limit_w": 300.0,
                "clock_core_mhz": 0,
                "clock_mem_mhz": 0,
                "vram_used_mb": 0,
                "vram_total_mb": 16303,
                "vram_percent": 0.0,
                "fan_percent": 0
            }

        try:
            util = pynvml.nvmlDeviceGetUtilizationRates(self.gpu_handle)
            temp = pynvml.nvmlDeviceGetTemperature(self.gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
            power_mw = pynvml.nvmlDeviceGetPowerUsage(self.gpu_handle)
            
            try:
                power_limit_mw = pynvml.nvmlDeviceGetEnforcedPowerLimit(self.gpu_handle)
                power_limit_w = power_limit_mw / 1000.0
            except Exception:
                power_limit_w = 300.0

            mem = pynvml.nvmlDeviceGetMemoryInfo(self.gpu_handle)
            core_clock = pynvml.nvmlDeviceGetClockInfo(self.gpu_handle, pynvml.NVML_CLOCK_GRAPHICS)
            mem_clock = pynvml.nvmlDeviceGetClockInfo(self.gpu_handle, pynvml.NVML_CLOCK_MEM)
            
            try:
                fan_p = pynvml.nvmlDeviceGetFanSpeed(self.gpu_handle)
            except Exception:
                fan_p = 0

            return {
                "model": self.gpu_name,
                "util_percent": util.gpu,
                "temp_c": temp,
                "power_w": power_mw / 1000.0,
                "power_limit_w": power_limit_w,
                "clock_core_mhz": core_clock,
                "clock_mem_mhz": mem_clock,
                "vram_used_mb": mem.used / (1024 * 1024),
                "vram_total_mb": mem.total / (1024 * 1024),
                "vram_percent": (mem.used / mem.total) * 100.0,
                "fan_percent": fan_p
            }
        except Exception as e:
            return {
                "model": self.gpu_name,
                "util_percent": 0,
                "temp_c": 0,
                "power_w": 0.0,
                "power_limit_w": 300.0,
                "clock_core_mhz": 0,
                "clock_mem_mhz": 0,
                "vram_used_mb": 0,
                "vram_total_mb": 16303,
                "vram_percent": 0.0,
                "fan_percent": 0,
                "error": str(e)
            }

    def _collect_memory(self):
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "total_gb": vm.total / (1024**3),
            "used_gb": vm.used / (1024**3),
            "free_gb": vm.available / (1024**3),
            "percent": vm.percent,
            "swap_used_gb": swap.used / (1024**3),
            "swap_total_gb": swap.total / (1024**3),
            "swap_percent": swap.percent
        }

    def _collect_disk(self, dt):
        root_usage = psutil.disk_usage('/')
        current_io = psutil.disk_io_counters()
        read_bytes_sec = 0.0
        write_bytes_sec = 0.0
        if self.last_disk_io and current_io:
            read_bytes_sec = max(0.0, (current_io.read_bytes - self.last_disk_io.read_bytes) / dt)
            write_bytes_sec = max(0.0, (current_io.write_bytes - self.last_disk_io.write_bytes) / dt)
        self.last_disk_io = current_io

        nvme_temp = 0.0
        try:
            temps = psutil.sensors_temperatures()
            if 'nvme' in temps and len(temps['nvme']) > 0:
                nvme_temp = temps['nvme'][0].current
        except Exception:
            pass

        return {
            "total_gb": root_usage.total / (1024**3),
            "used_gb": root_usage.used / (1024**3),
            "percent": root_usage.percent,
            "read_mb_s": read_bytes_sec / (1024 * 1024),
            "write_mb_s": write_bytes_sec / (1024 * 1024),
            "temp_c": nvme_temp
        }

    def _collect_network(self, dt):
        current_net = psutil.net_io_counters()
        down_bytes_sec = 0.0
        up_bytes_sec = 0.0
        if self.last_net_io and current_net:
            down_bytes_sec = max(0.0, (current_net.bytes_recv - self.last_net_io.bytes_recv) / dt)
            up_bytes_sec = max(0.0, (current_net.bytes_sent - self.last_net_io.bytes_sent) / dt)
        self.last_net_io = current_net

        return {
            "down_mb_s": down_bytes_sec / (1024 * 1024),
            "up_mb_s": up_bytes_sec / (1024 * 1024),
            "down_kb_s": down_bytes_sec / 1024,
            "up_kb_s": up_bytes_sec / 1024,
            "total_recv_gb": current_net.bytes_recv / (1024**3) if current_net else 0.0,
            "total_sent_gb": current_net.bytes_sent / (1024**3) if current_net else 0.0,
            "iface": self.cached_net_iface["iface"],
            "ip": self.cached_net_iface["ip"]
        }

    def _collect_motherboard(self):
        mobo = dict(self.cached_mobo)
        mobo_temp = 38.0
        try:
            temps = psutil.sensors_temperatures()
            if 'it8686' in temps and len(temps['it8686']) > 0:
                mobo_temp = temps['it8686'][0].current
        except Exception:
            pass
        mobo["temp_c"] = mobo_temp
        return mobo

    def _collect_audio(self):
        volume_pct = 30
        is_muted = False
        device_name = "USB Audio Speakers"

        try:
            res = subprocess.run(
                ["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"],
                capture_output=True, text=True, timeout=0.15
            )
            if res.returncode == 0:
                out = res.stdout.strip()
                # 예: "Volume: 0.30 [MUTED]" 또는 "Volume: 0.30"
                parts = out.split()
                if len(parts) >= 2:
                    val_str = parts[1]
                    volume_pct = int(float(val_str) * 100)
                if "[MUTED]" in out:
                    is_muted = True
        except Exception:
            pass

        return {
            "device": device_name,
            "volume_percent": volume_pct,
            "muted": is_muted
        }

    def _collect_top_processes(self):
        proc_list = []
        try:
            for p in sorted(psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']),
                            key=lambda x: x.info.get('cpu_percent') or 0,
                            reverse=True)[:5]:
                info = p.info
                name = info['name'] or 'unknown'
                if len(name) > 15:
                    name = name[:14] + "…"
                proc_list.append({
                    "pid": info['pid'],
                    "name": name,
                    "cpu_percent": info['cpu_percent'] or 0.0,
                    "mem_percent": info['memory_percent'] or 0.0
                })
        except Exception:
            pass
        return proc_list

    def _collect_system_meta(self):
        uptime_sec = time.time() - psutil.boot_time()
        hours = int(uptime_sec // 3600)
        minutes = int((uptime_sec % 3600) // 60)
        seconds = int(uptime_sec % 60)
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0.0, 0.0, 0.0)

        return {
            "uptime_str": f"{hours:02d}h {minutes:02d}m {seconds:02d}s",
            "load_1m": load_avg[0],
            "load_5m": load_avg[1],
            "load_15m": load_avg[2]
        }
