# Sys_Dash: AIDA64 하이엔드 슈퍼카 스타일 하드웨어 텔레메트리 대시보드

이 프로젝트는 게이밍 및 시스템 집중 작업 중 서브 모니터(`HDMI-A-1`, ARZOPA 2560x1440 144Hz)에 전체화면으로 시스템의 세부정보를 실시간 모니터링하기 위한 고성능 네이티브 데스크톱 HUD 대시보드입니다.

---

## 1. 하드웨어 및 시스템 사양

- **CPU**: AMD Ryzen 7 9800X3D (8-Core / 16-Thread, 부스트 최대 ~5.2GHz, 96MB 3D V-Cache)
- **GPU**: NVIDIA GeForce RTX 5070 Ti 16GB GDDR7 (Blackwell GB203 아키텍처, 300W TGP)
- **RAM**: DDR5 64GB
- **Target Display**: `HDMI-A-1` (ARZOPA 2560x1440 @ 144Hz, Scale 1.25)
- **OS / Window Manager**: Arch Linux / Hyprland (Wayland)

---

## 2. 주요 비주얼 및 시각화 요소 (AIDA64 / 슈퍼카 클러스터)

1. **듀얼 타이탄 타코미터 다이얼 (Titan Dial)**:
   - 좌/우 상단에 지름 300px 이상의 웅장한 대형 슈퍼카 타코미터 배치.
   - `0`, `20`, `40`, `60`, `80`, `100` 계측기 스케일 마킹 및 날렵한 네온 바늘(Needle).
   - **44pt 초대형 빅 넘버(Big-Number)**로 게임 중 곁눈질(0.1초)만으로도 부하율(%)과 온도(°C) 즉시 파악.
   - 80°C 이상 과열 시 패널 전체 붉은색 네온 펄스 자동 경고 발광.
2. **중앙 슈퍼카 파워 & 메모리 클러스터**:
   - GPU 실시간 소비전력 (TGP Wattage / 300W Cap) 대형 네온 바 게이지.
   - DDR5 64GB RAM & GDDR7 16GB VRAM 듀얼 세그먼트 레벨 바.
   - NVMe SSD 실시간 R/W 속도 & 센서 온도, 네트워크 2.5GbE 트래픽 박스.
3. **Ryzen 9800X3D Zen 5 실리콘 다이 매트릭스 (CCD 0)**:
   - 실제 프로세서 다이 구조를 형상화한 8개 독립 물리 코어 블록 (`CORE #00` ~ `CORE #07`, 4열 2행).
   - 코어별 실시간 부스트 클럭(최대 5.2GHz) 및 개별 SMT 스레드(T00 ~ T15) 세그먼트 바.
   - 코어 평균 부하율에 따른 실리콘 칩 배경 틴트 발광.
4. **초광폭 60초 실시간 오실로스코프 & 프로세스 센티넬**:
   - CPU vs GPU 부하율을 60초간 비교하는 초광폭 네온 베지어 곡선 및 그라디언트 파형.
   - 하단 TOP 5 프로세스 실시간 점유율 HUD 테이블.
5. **사이버네틱 메카닉 디자인 디테일**:
   - 배경의 은은한 헥사곤(벌집) 메쉬 텍스처.
   - 4개 모서리 육각 볼트 마킹 및 챔퍼 테두리, 상태 LED.

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
├── .venv/                   # Python 가상환경
├── main.py                  # 메인 윈도우 및 모니터 타겟팅 로직 (슈퍼카 클러스터 레이아웃)
├── monitor_collector.py     # 센서 비동기 수집 스레드 (NVML, psutil, lm_sensors)
├── theme.py                 # 사이버네틱 헥사곤 메쉬, 볼트 및 테마 유틸
├── widgets/
│   ├── __init__.py
│   ├── titan_dial.py        # 슈퍼카 타이탄 타코미터 다이얼 (바늘 & 대형 빅 넘버)
│   ├── power_cluster.py     # 중앙 GPU 전력 & 메모리 & I/O 클러스터
│   ├── silicon_die_matrix.py# Ryzen 9800X3D 8-Core / 16-Thread 실리콘 다이 매트릭스
│   ├── wide_stream_graph.py # 초광폭 60초 오실로스코프 & 프로세스 통합 위젯
│   ├── process_table.py     # TOP 5 프로세스 HUD 테이블
│   ├── stat_card.py         # 헥사곤 메쉬 & 볼트 메카닉 패널 테두리
│   └── header_bar.py        # 상단 HUD 시계 및 텔레메트리 헤더
├── run_dashboard.sh         # 원클릭 실행 래퍼 스크립트
├── sys-dash.desktop         # 데스크톱 애플리케이션 런처 등록 파일
├── dashboard_preview.png    # 렌더링 프리뷰 스크린샷
└── GEMINI.md                # 본 문서
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

Hyprland 환경에서 대시보드가 항상 `HDMI-A-1`의 9번 워크스페이스에 전체화면으로 고정되도록 하려면 `~/.config/hypr/hyprland.conf`에 다음 윈도우 규칙을 추가할 수 있습니다:

```ini
# SysDash 윈도우 규칙
windowrulev2 = monitor HDMI-A-1, class:^(sys-dash)$
windowrulev2 = workspace 9, class:^(sys-dash)$
windowrulev2 = fullscreen, class:^(sys-dash)$
```
