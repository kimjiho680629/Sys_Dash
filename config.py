import sys
import os

def get_resource_path(relative_path: str) -> str:
    """
    PyInstaller 번들 환경(sys._MEIPASS) 및 일반 파이썬 실행 환경 모두 지원하는 절대경로 반환
    """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)


class Config:
    # ==========================================
    # 1. 디스플레이 & 모니터 설정
    # ==========================================
    TARGET_MONITOR = "HDMI-A-1"       # 타겟 서브 모니터 (ARZOPA 2K 144Hz)
    START_FULLSCREEN = True           # 실행 시 즉시 전체화면 여부
    AUTO_DPI_SCALE = True             # 고해상도 DPI 자동 스케일링

    # ==========================================
    # 2. 텔레메트리 센서 수집 주기 & 임계값
    # ==========================================
    POLL_INTERVAL_MS = 800            # 백그라운드 센서 데이터 수집 주기 (ms)
    TEMP_WARNING_C = 68.0             # 주의 온도 (°C, 골드 앰버 표시)
    TEMP_CRITICAL_C = 80.0            # 과열 경고 온도 (°C, 네온 레드 펄스 발광)
    
    LOAD_WARNING_PCT = 60.0           # 고부하 주의 로드율 (%)
    LOAD_CRITICAL_PCT = 85.0          # 극한 부하 경고 로드율 (%)
    
    GPU_POWER_LIMIT_W = 300.0         # RTX 5070 Ti TGP 파워 캡 (W)

    # ==========================================
    # 3. 비주얼 테마 및 디자인 설정
    # ==========================================
    DEFAULT_THEME = "dark"            # 기본 테마 ("dark" 또는 "light")
    SHOW_HEXAGON_MESH = True          # 배경 헥사곤(벌집) 메쉬 텍스처 표시 여부
    SHOW_CORNER_BOLTS = True          # 4방향 코너 육각 볼트 마킹 표시 여부
    ROTATING_RING_ANIMATION = True    # 타코미터 내부 회전 링 애니메이션 활성화
    GRAPH_HISTORY_POINTS = 80         # 실시간 오실로스코프 파형 버퍼 포인트 수 (초 단위)


class HardwareConfig:
    """
    ==========================================================================
    하드웨어 스펙 커스텀 설정 (하이브리드 모드):
    - None 으로 설정하면: 시스템 커널(/proc, sysfs), DMI, NVML, psutil에서 자동 감지합니다.
    - 문자열이나 숫자를 지정하면: 시스템 감지값을 무시하고 지정한 내용으로 화면에 표시됩니다.
    ==========================================================================
    """
    # -------------------------------------------------------------------------
    # [1. 프로세서 (CPU)]
    # -------------------------------------------------------------------------
    # None: /proc/cpuinfo 에서 자동 인식 (예: "AMD Ryzen 7 9800X3D", "Intel Core i7-14700K")
    CPU_MODEL = None
    # None: CPU 최대 클럭 자동 감지 (MHz 단위)
    CPU_MAX_CLOCK_MHZ = None
    # None: CPU 설계 전력 자동 추정 (W 단위)
    CPU_TDP_W = None
    # None: L3 캐시 크기 자동 감지 (예: "3D V-Cache (96MB L3)", "L3 Cache (32MB)")
    CPU_CACHE_LABEL = None

    # -------------------------------------------------------------------------
    # [2. 그래픽카드 (GPU)]
    # -------------------------------------------------------------------------
    # None: NVML 및 PCI 서브시스템을 통해 실제 GPU 모델명 자동 감지 (예: "INNO3D RTX 5070 Ti", "RTX 4080 SUPER")
    GPU_MODEL = "INNO3D RTX 5070 Ti"
    # None: 최대 부스트 클럭 자동 지정 (MHz 단위)
    GPU_MAX_CLOCK_MHZ = None
    # None: NVML TGP 전력 한도 자동 감지 (W 단위)
    GPU_TGP_W = None
    # None: VRAM 실용량 기반 자동 표기 (예: "VRAM (GDDR7 16GB)")
    GPU_VRAM_LABEL = None

    # -------------------------------------------------------------------------
    # [3. 시스템 메모리 (RAM)]
    # -------------------------------------------------------------------------
    # RAM 모델/브랜드 표기 (None 시 "DDR5 High-Speed Memory" 자동)
    RAM_MODEL = "ADATA XPG LANCER RGB"
    # RAM 세부 타이밍 및 스펙 표기 (None 시 "Dual-Channel | High Speed" 자동)
    RAM_SPEC = "DDR5-6000  |  30-36-36-76  |  1.35V"

    # -------------------------------------------------------------------------
    # [4. 메인보드 (Motherboard)]
    # -------------------------------------------------------------------------
    # None: DMI(/sys/class/dmi/id/board_name)에서 자동 감지 (예: "GIGABYTE B850I AORUS PRO")
    MOBO_NAME = None
    # None: BIOS 버전 및 PCIe 버스 상태 자동 포맷팅
    MOBO_SUB = None

    # -------------------------------------------------------------------------
    # [5. NVMe SSD 스토리지]
    # -------------------------------------------------------------------------
    # None: /sys/block/nvme*/device/model 에서 실제 장착된 SSD 모델명 자동 감지
    SSD_MODEL = None
    # SSD 인터페이스 및 읽기 속도 스펙 라벨 (None 시 "PCIe Gen4 x4 NVMe SSD" 자동)
    SSD_SPEC = "PCIe Gen4 x4  |  7,000 MB/s"

    # -------------------------------------------------------------------------
    # [6. 네트워크 게이트웨이 / 공유기]
    # -------------------------------------------------------------------------
    # 공유기 또는 라우터 명칭 (예: "ASUS ROG GT-AX11000", "Wi-Fi 6E Gaming Router")
    ROUTER_MODEL = "ASUS ROG GT-AX11000"

    # -------------------------------------------------------------------------
    # [7. 오디오 시스템]
    # -------------------------------------------------------------------------
    AUDIO_ENGINE = "PipeWire Master Audio"
    # None: 현재 기본 출력 오디오 장치명 자동 감지 (예: "USB Audio Speakers")
    AUDIO_DEVICE = None

