# Sys_Dash: AIDA64 화이트 PCB 회로 기판 스타일 하드웨어 센서 패널

이 프로젝트는 게이밍 및 시스템 집중 작업 중 서브 모니터(`HDMI-A-1`, ARZOPA 2560x1440 144Hz)에 전체화면으로 시스템의 세부정보를 실시간 모니터링하기 위한 고성능 네이티브 데스크톱 AIDA64 스타일 센서 패널입니다.

---

## 1. 하드웨어 및 시스템 사양

- **CPU**: AMD Ryzen 7 9800X3D (8-Core / 16-Thread, 부스트 최대 ~5.2GHz, 96MB 3D V-Cache)
- **GPU**: NVIDIA GeForce RTX 5070 Ti 16GB GDDR7 (Blackwell GB203 아키텍처, 300W TGP)
- **RAM**: DDR5 64GB (Trident Z RGB 스타일 듀얼 채널)
- **Storage**: Samsung 980 Pro / PM9A1 PCIe Gen4 NVMe SSD
- **Target Display**: `HDMI-A-1` (ARZOPA 2560x1440 @ 144Hz, Scale 1.25)
- **OS / Window Manager**: Arch Linux / Hyprland (Wayland)

---

## 2. 주요 비주얼 및 컴포넌트 구성 (레퍼런스 100% 일치 화이트 PCB)

1. **배경 & 테마**:
   - 오프화이트/실버의 절차적 **PCB 회로 기판(Circuit Board) 트레이스 라인 및 비아 패드** 패턴.
   - 짙은 슬레이트 챠콜(`BORDER_MAIN`)의 정밀 테두리와 플랫 챠콜 프로그레스 바.
2. **CPU 섹션 (좌측 컬럼)**:
   - `Ryzen 7 9800X3D` 헤더 및 실시간 부스트 클럭(5.2GHz) 프로그레스 바.
   - **8개 물리 코어 각각의 실시간 미니 오실로스코프 그래프** (0~100 눈금, 실시간 파형).
   - 우측 상단 **CPU 소켓 패키지 배지** (소켓 핀 + 블루/바이올렛 다이 그라디언트 + 대형 흰색 온도 `50°C`).
   - `Core Voltage`, `CPU Package Power`, `3D V-Cache (96MB L3)` 할당 바.
   - `CPU Temperature Trend (60s)` 60초 온도 추이 오실로스코프.
   - 하단 서멀 배지: `Liquid Temp` (물방울), `VRM Temp` (모스펫 IC 칩), `PCH Temp` (칩셋).
3. **중앙 섹션 (메모리 / 시계 / 스토리지 / 쿨링)**:
   - **`Trident Z RGB (DDR5 64GB)`**: 상단 화려한 RGB 라이트 바 모듈 + 실시간 사용량 및 세부 타이밍 스펙.
   - **사선 챔퍼 시계 바**: 영문 디지털 시계(`12:34 AM`) + 게이밍 엠블럼 로고 + 날짜(`YYYY-MM-DD`).
   - **스토리지(SSD)**: M.2/2.5" SSD 아이콘 + C: 드라이브 점유 바 + 실시간 I/O 활동 오실로스코프.
   - **쿨링 팬 & 네트워크**: 회전하는 쿨링 팬 아이콘 (`CPU: 1140 RPM`, `GPU: 0%`) + 실시간 업/다운로드 대역폭.
4. **GPU 섹션 (우측 컬럼)**:
   - `GeForce RTX 5070 Ti` 헤더 및 코어 클럭(최대 2550MHz) 바.
   - **GPU Utl & FPS 듀얼 오실로스코프 그래프** (실시간 부하율 및 144Hz 프레임레이트).
   - 우측 상단 **그래픽카드 배지** (회전 쿨링 팬 + X자형 네온 RGB + 대형 흰색 온도 `35°C`).
   - `VRAM (GDDR7 16GB)`, `GDDR7 Memory Clock (14,001 MHz)`, `Core Voltage`, `Package Power (TGP 300W Cap)`.
   - 하단: `TOP 5 RESOURCE SENTINEL (ACTIVE TASKS)` 프로세스 점유율 HUD 테이블.

---

## 3. 기술 스택 및 아키텍처

- **언어 / 런타임**: Python 3.14 (Virtual Environment `.venv`)
- **GUI 프레임워크**: PyQt6 (하드웨어 가속 QPainter 렌더링, 60 FPS 보간 애니메이션)
- **센서 수집 백엔드**:
  - `nvidia-ml-py`: 프로세스 fork/exec 없이 공유 라이브러리(C 바인딩)로 GPU 센서 직접 호출 (오버헤드 0%)
  - `psutil`: 최적화된 C 확장을 통한 CPU 코어별 클럭, RAM, 스토리지 I/O, 네트워크 대역폭 및 프로세스 수집
  - `k10temp` & `it8686`: Linux hwmon 커널 센서 인터페이스 직접 연동
- **비동기 스레딩**: `SystemMonitorCollector (QThread)`를 통해 백그라운드 수집을 수행하여 UI 렌더링 스레드의 프레임 드랍을 원천 차단

---

## 4. 디렉토리 구조

```
/home/kjh/Projects/Gemini_Job/Sys_Dash/
├── .venv/                      # Python 가상환경
├── main.py                     # 메인 윈도우 및 3단 PCB 레이아웃
├── config.py                   # 사용자 설정 모듈 (주기, 모니터 등)
├── monitor_collector.py        # 센서 비동기 수집 스레드 (NVML, psutil, lm_sensors)
├── theme.py                    # 화이트 PCB 회로 기판 테마 및 컬러 팔레트
├── widgets/
│   ├── __init__.py
│   ├── pcb_components.py       # CPU 소켓, GPU 카드, 물방울, VRM, Trident Z, SSD, 팬 배지
│   ├── pcb_cpu_section.py      # 좌측: CPU 9800X3D, 8코어 오실로스코프, 서멀
│   ├── pcb_center_section.py   # 중앙: Trident Z RGB RAM, 시계 바, SSD, 팬/네트워크
│   ├── pcb_gpu_section.py      # 우측: RTX 5070 Ti, GPU/FPS 오실로스코프, VRAM, 프로세스
│   ├── mini_scope.py           # 0~100 눈금 미니 오실로스코프 파형 그래프
│   ├── pcb_bar.py              # 챠콜 그레이 플랫 프로그레스 바
│   ├── pcb_panels.py           # 패널 프레임 및 사선 챔퍼 시계 바
│   └── process_table.py        # 화이트 PCB 스타일 TOP 5 프로세스 테이블
├── run_dashboard.sh            # 원클릭 실행 래퍼 스크립트
├── sys-dash.desktop            # 데스크톱 애플리케이션 런처 등록 파일
├── dashboard_preview.png       # 렌더링 프리뷰 스크린샷
└── GEMINI.md                   # 본 문서
```

---

## 5. 실행 및 단축키

### 실행 방법
```bash
./run_dashboard.sh
```

### 단축키 안내
- `F11`: 전체화면(FullScreen) 토글
- `M`: 모니터 전환 (HDMI-A-1 <-> 메인 모니터 순환)
- `ESC` 또는 `Q`: 대시보드 종료

---

## 6. Hyprland 환경 최적화 팁

`~/.config/hypr/hyprland.conf`에 다음 윈도우 규칙을 추가하여 `HDMI-A-1`의 9번 워크스페이스에 고정할 수 있습니다:

```ini
windowrulev2 = monitor HDMI-A-1, class:^(sys-dash)$
windowrulev2 = workspace 9, class:^(sys-dash)$
windowrulev2 = fullscreen, class:^(sys-dash)$
```
