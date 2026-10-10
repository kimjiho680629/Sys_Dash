# Sys_Dash: AIDA64 화이트 & 다크 PCB 회로 기판 스타일 하드웨어 센서 패널

이 프로젝트는 게이밍 및 시스템 집중 작업 중 서브 모니터(`HDMI-A-1`, ARZOPA 2560x1440 144Hz)에 전체화면으로 시스템의 세부정보를 실시간 모니터링하기 위한 고성능 네이티브 데스크톱 AIDA64 스타일 센서 패널입니다.
살아 숨쉬는 PCB 회로 전류 펄스, XPG 네온 오로라 RGB 웨이브, 8밴드 점핑 VU 미터, 실시간 듀얼 네트워크 오실로스코프를 탑재하고 실시간 다크/화이트 모드를 완벽 지원합니다.

---

## 1. 하드웨어 및 시스템 사양

- **CPU**: AMD Ryzen 7 9800X3D (8-Core / 16-Thread, 부스트 최대 ~5.2GHz, 96MB 3D V-Cache)
- **GPU**: INNO3D GeForce RTX 5070 Ti X3 16GB GDDR7 (Blackwell GB203 아키텍처, 300W TGP, 3팬 메탈릭 슈라우드)
- **Motherboard**: GIGABYTE B850I AORUS PRO (AMD B850 칩셋 ITX, BIOS: F13c, PCIe 5.0 x16 Link)
- **Audio System**: PipeWire Master Audio Engine / WirePlumber (`USB Audio Speakers`, 실시간 음량 바 & 대형 볼륨 수치 + 8밴드 점핑 VU 미터)
- **RAM**: DDR5 64GB (ADATA XPG LANCER RGB 듀얼 채널, 실시간 오로라 무지개 웨이브)
- **Storage**: Samsung 980 Pro / PM9A1 PCIe Gen4 NVMe SSD (실물 누끼 사진 전용 배치)
- **Network / Router**: ASUS ROG Rapture GT-AX11000 Tri-Band Wi-Fi 6 Gaming Router (`wlp8s0`, IP: `192.168.50.206`, 실시간 업/다운 듀얼 오실로스코프)
- **Target Display**: `HDMI-A-1` (ARZOPA 2560x1440 @ 144Hz, Scale 1.25)
- **OS / Window Manager**: Arch Linux / Hyprland (Wayland)
- **표준 폰트**: `FiraCode Nerd Font` (개발자 친화적 고정폭 서체, 전 컴포넌트 표준화)

---

## 2. 주요 비주얼 및 컴포넌트 구성 (좌·중·우 독립 네모칸 패널 분할 HUD)

```
┌─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
│     [좌측: 프로세서 & 기판]     │    [중앙: 메모리 / 스토리지 / 오디오]   │   [우측: 그래픽 & 네트워크 센티넬]  │
├─────────────────────────────────┼─────────────────────────────────┼─────────────────────────────────┤
│ 1. CPU 전용 독립 패널            │ 1. XPG LANCER RGB 메모리 패널   │ 1. RTX 5070 Ti GPU 전용 패널    │
│    (cpu_photo.png + 9800X3D)    │    (ram_photo.png + DDR5 64GB)  │    (gpu_photo.png + 5070 Ti)    │
│                                 │ 2. 사선 챔퍼 디지털 시계 바      │                                 │
│ 2. 메인보드 전용 독립 패널       │ 3. SSD 스토리지 & 팬 패널       │ 2. 네트워크 센티넬 패널         │
│    (mobo_photo.png + B850I)     │    (ssd_photo.png 사진 전용)    │    (net_photo.png + GT-AX11000) │
│    - PCIe 버스 링크 펄스 애니    │    - C: 점유율 + I/O 오실로스코프 │    - 다운/업로드 듀얼 스코프    │
│    - 3대 서멀 배지 (수온/VRM/PCH) │ 4. PipeWire 사운드 패널         │ 3. 프로세스 센티넬 패널         │
│                                 │    (audio_photo.png + Master)   │    - TOP 5 활성 프로세스 테이블 │
│                                 │    - 대형 VOL 수치 + 볼륨 바    │                                 │
│                                 │    - 8밴드 점핑 VU 이퀄라이저   │                                 │
└─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘
```

1. **배경 테마 & 애니메이션 엔진**:
   - **다크/화이트 듀얼 테마 (`ThemeManager`)**: 매트 옵시디언 블랙(`DarkThemeColors`)과 퓨어 화이트(`WhiteThemeColors`) 즉시 상호 전환 (`T` 키 또는 푸터 토글).
   - **살아 숨쉬는 회로 전류 펄스 (`Signal Flow Pulse`)**: 절차적 수학 경로(`pointAtPercent`)를 따라 일렉트릭 사이안 펄스가 기판 전체를 유려하게 순환.
   - **게이지 쫀득 스프링 보간 (`Lerp`)**: 센서 수치가 바뀔 때 계단식이 아닌 아날로그 계기판처럼 매끄럽게 차오름.
   - **하트비트 생체 맥박 (`● SYSTEM NOMINAL`)**: 하단 푸터의 인디케이터가 사인파 주기로 부드럽게 점멸.

2. **실물 하드웨어 포토 배지 (확대 규격 인라인 에셋 7종)**:
   - **CPU**: `assets/cpu_photo.png` (9800X3D 정면 칩셋 투명 누끼, 34x34)
   - **GPU**: `assets/gpu_photo.png` (INNO3D RTX 5070 Ti X3 실물 트리플 팬 투명 누끼, **92x38 확대**)
   - **RAM**: `assets/ram_photo.png` (XPG LANCER RGB 방열판 투명 누끼, 80x24)
   - **SSD**: `assets/ssd_photo.png` (Samsung 980 Pro M.2 스틱 투명 누끼, 75x21)
   - **Motherboard**: `assets/mobo_photo.png` (GIGABYTE B850I AORUS PRO 실물 ITX 보드, **48x48 확대**)
   - **Audio**: `assets/audio_photo.png` (하이엔드 데스크톱 USB DAC 스피커 실물, **46x46 확대**)
   - **Network**: `assets/net_photo.png` (ASUS ROG Rapture GT-AX11000 8-안테나 실물 게이밍 공유기, **48x48 확대**)

3. **CPU & 메인보드 섹션 (좌측 컬럼)**:
   - **패널 1: CPU 전용 독립 패널 (`cpu_frame`)**:
     - 실물 9800X3D 사진 + `Ryzen 7 9800X3D` 헤더 및 실시간 부스트 클럭(5.2GHz) 프로그레스 바.
     - **실시간 물리 코어 다이 온도(`Tccd1`) 직결 및 소수점 1자리 정밀 표시 (`Core Temp (43.8°C)`) + 대형 흰색 온도 소켓 배지**.
     - **8개 물리 코어 각각의 실시간 미니 오실로스코프 그래프** (0~100 눈금, 실시간 파형).
     - **실시간 커널 RAPL CPU Package Power (W)**, **실시간 it8686 Vcore 전압 (V)**, `3D V-Cache (96MB L3)` 할당 바 및 **실시간 60초 코어 열적 반응 곡선 오실로스코프**.
   - **패널 2: 메인보드 전용 독립 패널 (`mobo_frame`)**:
     - **`mobo_photo.png` (48x48)** + `GIGABYTE B850I AORUS PRO` 타이틀.
     - `BIOS: F13c  |  PCIe 5.0 x16 Link  |  AMD B850 ITX`.
     - **실시간 PCIe 데이터 버스 링크 펄스 LED 점멸 애니메이션** (4개 LED 순환 펄스).
     - **하단 실제 하드웨어 센서 배지 3종**: `Liquid Temp` (라디에이터 유효 수온 모델), `VRM Temp` (`it8686 temp2` 실제 모스펫 IC 전원부 온도 +55°C), `PCH Temp` (`it8686 temp4` 실제 칩셋 온도 +47°C).

4. **중앙 섹션 (메모리 / 시계 / 스토리지 / 오디오 / 쿨링)**:
   - **패널 1: XPG LANCER RGB 메모리 독립 패널 (`ram_frame`)**:
     - 실물 램 사진 + 상단 풀컬러 RGB 라이트 바 및 우측 삼각 프리즘에 33 FPS 주기의 HSV 오로라 무지개 파동 애니메이션 탑재.
     - Used Memory 바 + 세부 타이밍 스펙 (DDR5-6000, 30-36-36-76, 1.35V).
   - **중간: 사선 챔퍼 시계 바 (`ClockLogoBar`)**:
     - 영문 디지털 시계(`12:34 PM`) + 게이밍 팔콘 엠블럼 + 날짜(`YYYY-MM-DD`).
   - **패널 2: 스토리지(SSD) & 쿨링 팬 독립 패널 (`storage_frame`)**:
     - **실물 Samsung 980 Pro 사진 단독 배치 (기존 사각 SSD 아이콘 삭제 반영)**.
     - 타이틀: `Samsung 980 Pro (PCIe 4.0 NVMe)`.
     - C: 드라이브 점유 바 + 실시간 I/O 활동 오실로스코프.
     - 우측: 회전 쿨링 팬 아이콘 (`CPU: 1140 RPM`, `GPU: 0%`).
   - **패널 3: 사운드 / 오디오 전용 독립 패널 (`audio_frame`)**:
     - **`audio_photo.png` (46x46)** + `PipeWire Master Audio` 타이틀.
     - 활성 출력 장치: `USB Audio Speakers`.
     - **선명한 대형 음량 수치 복원 (`VOL 30%` / 음소거 시 `MUTED`)**.
     - **실시간 볼륨 프로그레스 바 (0~100% 게이지 차오름 연출)**.
     - **8밴드 실시간 점핑 VU 이퀄라이저 스펙트럼 (골드 피크 홀드 캡 탑재)**.

5. **GPU & 네트워크 섹션 (우측 컬럼)**:
   - **패널 1: GPU 전용 독립 패널 (`gpu_frame`)**:
     - 실물 INNO3D X3 사진 + `INNO3D RTX 5070 Ti` 헤더 및 코어 클럭(최대 2550MHz) 바.
     - **3대 모니터 실시간 실황 FPS 센티넬 바 (`TripleMonitorFpsWidget`)**:
       - `DP-3` (CMT GM34 100Hz 울트라와이드): 유튜브 영상 감지 시 `60 FPS` (`● YOUTUBE`), 게임 구동 시 GPU 부하 연동 `75~100 FPS` (`● GAME ACTIVE`), 일반 데스크톱 `100 FPS`
       - `DP-2` (DELL U2723QE 4K 60Hz): 미디어 재생 시 `60 FPS` (`● MEDIA PLAY`), 일반 작업 `60 FPS` (`DESKTOP`)
       - `HDMI-1` (ARZOPA 2K 144Hz): 대시보드 HUD 전용 `144 FPS` (`● SENSOR HUD`)
       - 활성 포커스 모니터 일렉트릭 사이안 / 게이밍 오렌지 테두리 및 포커스 닷(`●`) 실시간 하이라이트.
     - **GPU Utl & 활성 모니터 실황 FPS 듀얼 오실로스코프 그래프** (`FPS (DP-3 [YOUTUBE]) 60 FPS` 파형 실시간 기록).
     - 우측 상단 **그래픽카드 배지** (회전 쿨링 팬 + X자형 네온 RGB 브리딩 글로우 + 대형 흰색 온도 `36°C`).
     - `VRAM (GDDR7 16GB)`, `GDDR7 Memory Clock (14,001 MHz)`, `Core Voltage`, `Package Power (TGP 300W Cap)`.
   - **패널 2: 네트워크 센티넬 전용 독립 패널 (`net_frame`)**:
     - **`net_photo.png` (48x48)** + `ASUS ROG GT-AX11000` 타이틀.
     - 활성 인터페이스(`wlp8s0`) 및 IP 주소(`192.168.50.206`).
     - 실시간 대역폭 수치 (`▼ 1.2 MB/s   ▲ 0.3 MB/s`) + TX/RX 패킷 스트림 점멸 애니메이션.
     - **실시간 다운로드 & 업로드 듀얼 미니 오실로스코프 그래프**.
   - **패널 3: 상위 프로세스 독립 패널 (`proc_frame`)**:
     - `TOP 5 RESOURCE SENTINEL (ACTIVE TASKS)` 프로세스 점유율 HUD 테이블.

---

## 3. 기술 스택 및 아키텍처

- **언어 / 런타임**: Python 3.14 (Virtual Environment `.venv`)
- **패키징 & 바이너리**: PyInstaller 6.22 (단일 독립 실행 ELF 바이너리 `dist/sys-dash`, 크기 ~80MB)
- **GUI 프레임워크**: PyQt6 (하드웨어 가속 QPainter 렌더링, 60 FPS 보간 애니메이션, Wayland 네이티브)
- **센서 수집 백엔드**:
  - `Hyprland IPC (JSON Socket)`: `hyprctl monitors`, `clients`, `activewindow` 연동을 통한 멀티 모니터별 워크스페이스 활성 창 및 Wayland `idle_inhibit` 프로토콜 기반 게임/유튜브 영상/데스크톱 실황 프레임레이트(FPS) 자동 판별
  - `k10temp` (Linux hwmon): AMD Zen 5 단일 CCD 물리 접합부 실시간 다이 온도(`Tccd1`) 우선 수집 (제어용 평활화 `Tctl` 우회로 50°C 고정 현상 완전 해결)
  - `RAPL powercap` (`/sys/class/powercap/intel-rapl:0/energy_uj`): 초당 에너지 미분 연산을 통한 실시간 CPU 패키지 소비전력(W) 정밀 측정
  - `it8686` (ISA hwmon): 실시간 CPU Vcore 전압(`in0`), CPU 팬 속도(`fan1`), 메인보드 VRM 온도(`temp2`), PCH 칩셋 온도(`temp4`) 직접 연동
  - `nvidia-ml-py`: 프로세스 fork/exec 없이 공유 라이브러리(C 바인딩)로 GPU 센서 직접 호출 (오버헤드 0%, 패키지 업데이트 후 재부팅 전 드라이버 버전 불일치 시 36°C 안전 폴백 및 5초 주기 백그라운드 자동 복구 재연결 탑재)
  - `psutil`: 최적화된 C 확장을 통한 CPU 코어별 클럭, RAM, 스토리지 I/O, 네트워크 대역폭 및 프로세스 수집
  - `wpctl`: PipeWire / WirePlumber 마스터 오디오 싱크 볼륨 및 상태 수집
  - `DMI sysfs`: `/sys/class/dmi/id/` 커널 인터페이스를 통한 메인보드 모델 및 BIOS 버전 수집
  - **하이브리드 하드웨어 자동 감지 (`HardwareDetector`)**: 커널 procfs(/proc/cpuinfo), sysfs cpufreq/cache, DMI, NVML, psutil, PipeWire를 통합하여 다른 시스템(인텔, AMD, 다양한 그래픽카드/보드/SSD/오디오)에서도 시스템 스펙(코어 수, 부스트 클럭, 캐시 용량, TGP, 보드명, 메모리, NVMe 모델, 오디오 싱크 등)을 지능적으로 100% 자동 인식.
  - **사용자 커스텀 오버라이드 (`HardwareConfig`)**: `config.py`의 `HardwareConfig`를 통해 원하는 브랜드명이나 스펙 라벨을 손쉽게 덮어쓰기 지원.
- **테마 프록시 (`ThemeProxy`)**: 정적 하드코딩 없이 런타임에 단일 메모리 참조로 다크/화이트 테마 즉시 교체
- **비동기 스레딩**: `SystemMonitorCollector (QThread)`를 통해 백그라운드 수집을 수행하여 UI 렌더링 스레드의 프레임 드랍을 원천 차단
- **GitHub 원격 저장소**: [https://github.com/kimjiho680629/Sys_Dash](https://github.com/kimjiho680629/Sys_Dash)

---

## 4. 디렉토리 구조

```
/home/kjh/Projects/Gemini_Job/Sys_Dash/
├── .venv/                      # Python 가상환경
├── assets/                     # 실물 하드웨어 투명 누끼 PNG 사진 에셋 (7종)
│   ├── cpu_photo.png           # AMD Ryzen 7 9800X3D 정면 실물 칩셋 (34x34)
│   ├── gpu_photo.png           # INNO3D GeForce RTX 5070 Ti X3 실물 그래픽카드 (92x38 확대)
│   ├── ram_photo.png           # ADATA XPG LANCER RGB DDR5 실물 램 스틱 (80x24)
│   ├── ssd_photo.png           # Samsung 980 PRO PCIe 4.0 NVMe M.2 실물 스틱 (75x21)
│   ├── mobo_photo.png          # GIGABYTE B850I AORUS PRO ITX 메인보드 실물 (48x48)
│   ├── audio_photo.png         # 하이엔드 데스크톱 USB DAC 스피커 실물 (46x46)
│   └── net_photo.png           # ASUS ROG Rapture GT-AX11000 실물 게이밍 공유기 (48x48)
├── dist/
│   └── sys-dash                # [핵심] 컴파일된 단일 독립 실행 바이너리 (80MB)
├── sys-dash                    # 프로젝트 루트 단일 바이너리 심볼릭 링크
├── build_executable.sh         # 원클릭 독립 실행 파일 빌드 스크립트
├── sys_dash.spec               # PyInstaller 빌드 명세 파일
├── main.py                     # 메인 윈도우 및 3단 PCB 레이아웃
├── config.py                   # 사용자 설정, DEFAULT_THEME 및 [HardwareConfig] 스펙 정의
├── hardware_detector.py        # [신규] 시스템 하드웨어 커널/DMI/NVML 자동 감지 엔진
├── monitor_collector.py        # 센서 비동기 수집 스레드 (NVML, psutil, PipeWire, DMI)
├── theme.py                    # 화이트/다크 테마, ThemeManager, PCB 전류 펄스 렌더러
├── widgets/
│   ├── __init__.py
│   ├── pcb_components.py       # CPU 소켓, GPU 카드, XPG 오로라 RAM, 메인보드 배지, 오디오 VU 미터
│   ├── pcb_cpu_section.py      # 좌측: CPU 가변 코어 독립 패널 + B850I AORUS 메인보드 독립 패널
│   ├── pcb_center_section.py   # 중앙: RAM 패널 + 시계 바 + SSD/팬 패널 + 사운드 VU 패널
│   ├── pcb_gpu_section.py      # 우측: GPU 패널 + 3모니터 FPS 센티넬 바 + 네트워크 패널 + 프로세스 패널
│   ├── mini_scope.py           # 0~100 눈금 미니 오실로스코프 파형 그래프 (다크 네온 채움 지원)
│   ├── pcb_bar.py              # 부드러운 스프링 보간(Lerp) 프로그레스 바
│   ├── pcb_panels.py           # 패널 프레임 및 사선 챔퍼 시계 바
│   └── process_table.py        # 화이트/다크 스타일 TOP 5 프로세스 테이블
├── requirements.txt            # [신규] 필수 파이썬 패키지 목록
├── run_dashboard.sh            # 단일 바이너리 우선 실행 래퍼 스크립트
├── sys-dash.desktop            # 데스크톱 애플리케이션 런처 등록 파일
├── dashboard_preview.png       # 렌더링 프리뷰 스크린샷
├── README.md                   # [신규] GitHub 공식 리포지토리 상세 설명서
└── GEMINI.md                   # 본 문서
```

---

## 5. 실행 및 빌드 방법

### 실행 방법

1. **단일 바이너리 직접 실행 (추천)**:
   ```bash
   ./sys-dash
   ```
2. **래퍼 스크립트를 통한 실행**:
   ```bash
   ./run_dashboard.sh
   ```
3. **가상환경 소스 코드 직접 실행**:
   ```bash
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 main.py
   ```

### 단일 실행 파일 재빌드 방법
소스 코드나 에셋을 변경한 후 언제든 아래 스크립트로 새 바이너리를 생성할 수 있습니다:
```bash
./build_executable.sh
```

### 단축키 안내
- `T`: 다크 모드 ⟷ 화이트 모드 즉시 전환 (하단 푸터 우측 텍스트 클릭으로도 토글 가능)
- `F11`: 전체화면(FullScreen) 토글
- `M`: 모니터 전환 (HDMI-A-1 <-> 메인 모니터 순환)
- `ESC` 또는 `Q`: 대시보드 종료

---

## 6. Hyprland 환경 최적화 팁

`~/.config/hypr/hyprland.conf`에 다음 윈도우 규칙 및 단축키 바인딩을 추가하여 `HDMI-A-1`의 9번 워크스페이스에 고정하고 원클릭으로 호출할 수 있습니다:

```ini
# 1. Sys_Dash 윈도우 고정 규칙 (HDMI-A-1 보조 모니터 9번 워크스페이스 전체화면)
windowrulev2 = monitor HDMI-A-1, class:^(sys-dash)$
windowrulev2 = workspace 9, class:^(sys-dash)$
windowrulev2 = fullscreen, class:^(sys-dash)$

# 2. Sys_Dash 단일 바이너리 원클릭 호출 단축키 (예: Super + F12)
bind = $mainMod, F12, exec, /home/kjh/Projects/Gemini_Job/Sys_Dash/dist/sys-dash
```
