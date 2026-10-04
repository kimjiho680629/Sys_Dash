"""
Sys_Dash: AIDA64 화이트 & 다크 PCB 스타일 하드웨어 텔레메트리 대시보드
AMD Ryzen 7 9800X3D + NVIDIA GeForce RTX 5070 Ti (GB203 16GB)
HDMI-A-1 (ARZOPA 2K 144Hz) 전용 네이티브 센서 패널
살아 숨쉬는 PCB 회로 전류 펄스 애니메이션 & 실시간 다크/화이트 모드 토글
"""

import sys
import os
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QKeyEvent, QColor

from theme import (
    WhitePCBColor, ThemeManager, draw_pcb_background, get_font_bold, get_font_regular
)
from config import Config
from monitor_collector import SystemMonitorCollector
from widgets.pcb_cpu_section import PcbCpuSection
from widgets.pcb_center_section import PcbCenterSection
from widgets.pcb_gpu_section import PcbGpuSection


class WhitePCBDashboard(QMainWindow):
    """
    화이트 & 다크 매트 PCB 회로 기판 AIDA64 센서 패널 대시보드
    """
    def __init__(self, target_monitor=None):
        super().__init__()
        self.target_monitor_name = target_monitor or Config.TARGET_MONITOR
        self.collector = None

        # 회로 전류 펄스 및 시스템 맥박 애니메이션 변수
        self.pulse_offset = 0.0
        self.pulse_dot_phase = 0.0

        # 초기 테마 설정 적용
        initial_theme = getattr(Config, "DEFAULT_THEME", "dark").lower()
        ThemeManager.set_theme(initial_theme)

        self._init_ui()
        self._setup_monitor()
        self._start_animations()
        self._start_collector()

        ThemeManager.register_listener(self.apply_theme)
        self.apply_theme()

    def _init_ui(self):
        # 중앙 위젯 (PCB 회로 기판 배경과 전류 펄스를 직접 페인팅)
        self.central_panel = QWidget(self)
        self.setCentralWidget(self.central_panel)

        def custom_paint(event):
            painter = QPainter(self.central_panel)
            draw_pcb_background(painter, self.central_panel.rect(), self.pulse_offset)

        self.central_panel.paintEvent = custom_paint

        root_layout = QVBoxLayout(self.central_panel)
        root_layout.setContentsMargins(18, 16, 18, 14)
        root_layout.setSpacing(12)

        # 메인 3단 컬럼 레이아웃 (Left: CPU, Center: RAM/SSD/FANS/CLOCK, Right: GPU/SENTINEL)
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(16)

        # 좌측: CPU 섹션
        self.cpu_section = PcbCpuSection(parent=self)
        columns_layout.addWidget(self.cpu_section, stretch=34)

        # 중앙: 메모리, 시계, I/O 및 쿨링 팬 섹션
        self.center_section = PcbCenterSection(parent=self)
        columns_layout.addWidget(self.center_section, stretch=32)

        # 우측: GPU 및 프로세스 섹션
        self.gpu_section = PcbGpuSection(parent=self)
        columns_layout.addWidget(self.gpu_section, stretch=34)

        root_layout.addLayout(columns_layout, stretch=1)

        # 하단 풋터 바
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(6, 0, 6, 0)

        # 시스템 맥박 점멸 인디케이터
        self.left_status = QLabel()
        self.left_status.setFont(get_font_regular(9))
        footer_layout.addWidget(self.left_status)

        footer_layout.addStretch()

        # 단축키 안내 및 원클릭 테마 토글 라벨
        self.hotkey_info = QLabel()
        self.hotkey_info.setFont(get_font_regular(9))
        self.hotkey_info.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hotkey_info.mousePressEvent = lambda e: self.toggle_theme()
        footer_layout.addWidget(self.hotkey_info)

        root_layout.addLayout(footer_layout)

    def _start_animations(self):
        # 1. PCB 전류 펄스 & 시스템 맥박 애니메이션 타이머 (30ms = 약 33 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._on_anim_tick)
        self.anim_timer.start(30)

    def _on_anim_tick(self):
        # 회로 전류 펄스 오프셋 증가
        self.pulse_offset = (self.pulse_offset + 0.005) % 1.0
        self.central_panel.update()

        # 하단 상태 표시줄의 살아 숨쉬는 맥박 펄스 (Heartbeat Dot)
        self.pulse_dot_phase = (self.pulse_dot_phase + 0.08) % (math.pi * 2)
        dot_pulse = (math.sin(self.pulse_dot_phase) + 1.0) / 2.0
        
        if ThemeManager.is_dark():
            dot_c = QColor(0, int(190 + 65 * dot_pulse), int(210 + 45 * dot_pulse))
        else:
            dot_c = QColor(0, int(160 + 50 * dot_pulse), int(80 + 40 * dot_pulse))

        self.left_status.setText(
            f"<span style='color: {dot_c.name()}; font-weight: bold;'>●</span> "
            f"<span style='color: {WhitePCBColor.TEXT_MUTED.name()};'>SYSTEM NOMINAL  |  ARCH LINUX  |  HYPRLAND DESKTOP</span>"
        )

    def apply_theme(self):
        mode_str = ThemeManager.get_theme().upper()
        self.setWindowTitle(f"AIDA64 SENSOR PANEL // {mode_str} PCB CIRCUIT HUD")

        c_muted = WhitePCBColor.TEXT_MUTED.name()
        c_main = WhitePCBColor.TEXT_MAIN.name()

        self.hotkey_info.setStyleSheet(f"color: {c_muted};")
        self.hotkey_info.setText(
            f"[F11] FULLSCREEN  |  [M] MONITOR  |  <span style='color: {c_main}; font-weight: bold;'>[T] THEME: {mode_str}</span>  |  [ESC / Q] EXIT"
        )

        self.central_panel.update()

    def toggle_theme(self):
        ThemeManager.toggle_theme()

    def _setup_monitor(self):
        screens = QApplication.screens()
        target_screen = None

        for s in screens:
            if self.target_monitor_name.lower() in s.name().lower():
                target_screen = s
                break

        if target_screen:
            print(f"[Dashboard] Targeting monitor: {target_screen.name()} with geom {target_screen.geometry()}")
            self.setScreen(target_screen)
            self.setGeometry(target_screen.geometry())
            self.windowHandle().setScreen(target_screen) if self.windowHandle() else None
            self.showFullScreen()
        else:
            print(f"[Dashboard] Target monitor '{self.target_monitor_name}' not found. Using default screen.")
            self.showFullScreen()

    def _start_collector(self):
        self.collector = SystemMonitorCollector(interval_ms=Config.POLL_INTERVAL_MS, parent=self)
        self.collector.data_ready.connect(self.on_data_updated)
        self.collector.start()

    def on_data_updated(self, data):
        cpu = data['cpu']
        gpu = data['gpu']
        mem = data['memory']
        disk = data['disk']
        net = data['network']
        mobo = data.get('motherboard', {})
        audio = data.get('audio', {})
        procs = data['processes']

        # 1. 좌측: CPU 및 메인보드 섹션 업데이트
        self.cpu_section.update_data(cpu, mobo)

        # 2. 중앙: 메모리, SSD, PipeWire 오디오 VU 미터 및 쿨링 팬 섹션 업데이트
        self.center_section.update_data(mem, disk, cpu['fan_rpm'], gpu['fan_percent'], audio)

        # 3. 우측: GPU, 네트워크 센티넬 듀얼 오실로스코프 및 프로세스 섹션 업데이트
        self.gpu_section.update_data(gpu, procs, net)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif key == Qt.Key.Key_M:
            self._switch_screen()
        elif key == Qt.Key.Key_T:
            self.toggle_theme()
        elif key in (Qt.Key.Key_Escape, Qt.Key.Key_Q):
            self.close()
        else:
            super().keyPressEvent(event)

    def _switch_screen(self):
        screens = QApplication.screens()
        if len(screens) <= 1:
            return
        curr_screen = self.screen()
        idx = screens.index(curr_screen) if curr_screen in screens else 0
        next_screen = screens[(idx + 1) % len(screens)]
        self.setScreen(next_screen)
        self.setGeometry(next_screen.geometry())
        self.showFullScreen()

    def closeEvent(self, event):
        if hasattr(self, 'anim_timer') and self.anim_timer.isActive():
            self.anim_timer.stop()
        if self.collector:
            self.collector.stop()
        event.accept()


def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("sys-dash")
    app.setDesktopFileName("sys-dash")
    app.setFont(get_font_regular(10))

    dashboard = WhitePCBDashboard(target_monitor="HDMI-A-1")
    dashboard.setObjectName("sys-dash")
    dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
