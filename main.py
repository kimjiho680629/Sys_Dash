"""
Sys_Dash: AIDA64 화이트 PCB 스타일 하드웨어 텔레메트리 대시보드
AMD Ryzen 7 9800X3D + NVIDIA GeForce RTX 5070 Ti (GB203 16GB)
HDMI-A-1 (ARZOPA 2K 144Hz) 전용 네이티브 센서 패널
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QKeyEvent

from theme import WhitePCBColor, draw_pcb_background, get_font_bold
from config import Config
from monitor_collector import SystemMonitorCollector
from widgets.pcb_cpu_section import PcbCpuSection
from widgets.pcb_center_section import PcbCenterSection
from widgets.pcb_gpu_section import PcbGpuSection


class WhitePCBDashboard(QMainWindow):
    """
    화이트 PCB 회로 기판 AIDA64 센서 패널 대시보드
    """
    def __init__(self, target_monitor=None):
        super().__init__()
        self.target_monitor_name = target_monitor or Config.TARGET_MONITOR
        self.collector = None

        self.setWindowTitle("AIDA64 SENSOR PANEL // WHITE PCB CIRCUIT HUD")

        self._init_ui()
        self._setup_monitor()
        self._start_collector()

    def _init_ui(self):
        # 중앙 위젯 (PCB 회로 기판 배경을 직접 페인팅)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        def custom_paint(event):
            painter = QPainter(central_widget)
            draw_pcb_background(painter, central_widget.rect())

        central_widget.paintEvent = custom_paint

        root_layout = QVBoxLayout(central_widget)
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

        left_status = QLabel("● SYSTEM NOMINAL  |  ARCH LINUX  |  HYPRLAND DESKTOP")
        left_status.setFont(get_font_bold(8))
        left_status.setStyleSheet(f"color: {WhitePCBColor.TEXT_MUTED.name()};")
        footer_layout.addWidget(left_status)

        footer_layout.addStretch()

        hotkey_info = QLabel("[F11] FULLSCREEN  |  [M] SWITCH MONITOR  |  [ESC / Q] EXIT")
        hotkey_info.setFont(get_font_bold(8))
        hotkey_info.setStyleSheet(f"color: {WhitePCBColor.TEXT_MUTED.name()};")
        footer_layout.addWidget(hotkey_info)

        root_layout.addLayout(footer_layout)

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
        procs = data['processes']

        # 1. CPU 섹션 업데이트
        self.cpu_section.update_data(cpu)

        # 2. 중앙 섹션 업데이트
        self.center_section.update_data(mem, disk, net, cpu['fan_rpm'], gpu['fan_percent'])

        # 3. GPU 섹션 업데이트
        self.gpu_section.update_data(gpu, procs)

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key == Qt.Key.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()
        elif key == Qt.Key.Key_M:
            self._switch_screen()
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
        if self.collector:
            self.collector.stop()
        event.accept()


def main():
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("sys-dash")
    app.setDesktopFileName("sys-dash")

    dashboard = WhitePCBDashboard(target_monitor="HDMI-A-1")
    dashboard.setObjectName("sys-dash")
    dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
