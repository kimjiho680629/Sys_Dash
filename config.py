"""
Sys_Dash 환경설정 모듈 (User Configuration)
대시보드의 모니터 타겟, 센서 주기, 임계값, 테마 옵션 등을 손쉽게 커스터마이징 가능
"""

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
    SHOW_HEXAGON_MESH = True          # 배경 헥사곤(벌집) 메쉬 텍스처 표시 여부
    SHOW_CORNER_BOLTS = True          # 4방향 코너 육각 볼트 마킹 표시 여부
    ROTATING_RING_ANIMATION = True    # 타코미터 내부 회전 링 애니메이션 활성화
    GRAPH_HISTORY_POINTS = 80         # 실시간 오실로스코프 파형 버퍼 포인트 수 (초 단위)
