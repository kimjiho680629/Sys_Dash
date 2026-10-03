"""
Sys_Dash: AIDA64 하이엔드 슈퍼카 스타일 하드웨어 텔레메트리 대시보드
AMD Ryzen 7 9800X3D (8C/16T) + NVIDIA GeForce RTX 5070 Ti (GB203 16GB)
HDMI-A-1 (ARZOPA 2K 144Hz) 전용 네이티브 HUD 시스템
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QScreen

from theme import HUDColor, get_font_mono, get_font_display
from config import Config
from monitor_collector import SystemMonitorCollector
from widgets.header_bar import HUDHeaderBar
from widgets.stat_card import HUDCard
from widgets.titan_dial import TitanDial
from widgets.power_cluster import PowerClusterWidget
from widgets.silicon_die_matrix import SiliconDieMatrix
from widgets.wide_stream_graph import WideGraphAndProcessWidget


class CyberpunkDashboard(QMainWindow):
    def __init__(self, target_monitor=None):
        super().__init__()
        self.target_monitor_name = target_monitor or Config.TARGET_MONITOR
        self.collector = None

        self.setWindowTitle("SYS_HUD // HIGH-PERFORMANCE SENSOR CLUSTER")
        self.setStyleSheet(f"background-color: {HUDColor.BG_VOID.name()}; color: {HUDColor.TEXT_TITLE.name()};")

        self._init_ui()
        self._setup_monitor()
        self._start_collector()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(14, 8, 14, 8)
        root_layout.setSpacing(8)

        # 1. 상단 HUD 헤더 바
        self.header_bar = HUDHeaderBar(self)
        root_layout.addWidget(self.header_bar)

        # ==========================================================
        # 2. 상단 섹션: 듀얼 타이탄 타코미터 & 중앙 파워 클러스터
        # ==========================================================
        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        # [좌측: CPU 패키지 타이탄 다이얼 카드]
        self.cpu_dial_card = HUDCard(title="// CPU PACKAGE TELEMETRY", tag="8C / 16T", parent=self)
        self.cpu_dial_card.set_accent_color(HUDColor.CYAN)
        self.cpu_dial = TitanDial(
            title="RYZEN 7 9800X3D", unit="%",
            max_val1=100.0, max_val2=100.0,
            primary_color=HUDColor.CYAN, secondary_color=HUDColor.PURPLE,
            parent=self.cpu_dial_card
        )
        self.cpu_dial_card.set_content_widget(self.cpu_dial)
        top_row.addWidget(self.cpu_dial_card, stretch=31)

        # [중앙: 슈퍼카 파워 & 메모리 클러스터 카드]
        self.center_card = HUDCard(title="// POWER & MEMORY SUBSYSTEM", tag="TGP DYNAMICS", parent=self)
        self.center_card.set_accent_color(HUDColor.GOLD)
        self.power_cluster = PowerClusterWidget(parent=self.center_card)
        self.center_card.set_content_widget(self.power_cluster)
        top_row.addWidget(self.center_card, stretch=38)

        # [우측: GPU 엔진 타이탄 다이얼 카드]
        self.gpu_dial_card = HUDCard(title="// GPU ENGINE TELEMETRY", tag="GB203 ARCH", parent=self)
        self.gpu_dial_card.set_accent_color(HUDColor.MAGENTA)
        self.gpu_dial = TitanDial(
            title="RTX 5070 Ti 16GB", unit="%",
            max_val1=100.0, max_val2=100.0,
            primary_color=HUDColor.MAGENTA, secondary_color=HUDColor.GOLD,
            parent=self.gpu_dial_card
        )
        self.gpu_dial_card.set_content_widget(self.gpu_dial)
        top_row.addWidget(self.gpu_dial_card, stretch=31)

        root_layout.addLayout(top_row, stretch=5)

        # ==========================================================
        # 3. 하단 섹션: 9800X3D 실리콘 다이 매트릭스 & 와이드 오실로스코프
        # ==========================================================
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)

        # [하단 좌측: Ryzen 실리콘 다이 8-Core / 16-Thread 매트릭스 카드]
        self.die_card = HUDCard(title="// AMD RYZEN ZEN 5 SILICON DIE MATRIX (CCD 0)", tag="SMT LOGIC", parent=self)
        self.die_card.set_accent_color(HUDColor.CYAN)
        self.die_matrix = SiliconDieMatrix(parent=self.die_card)
        self.die_card.set_content_widget(self.die_matrix)
        bottom_row.addWidget(self.die_card, stretch=48)

        # [하단 우측: 60초 와이드 오실로스코프 & 프로세스 센티넬 카드]
        self.graph_card = HUDCard(title="// REALTIME 60s OSCILLOSCOPE & TASK SENTINEL", tag="LIVE STREAM", parent=self)
        self.graph_card.set_accent_color(HUDColor.GREEN)
        self.wide_graph = WideGraphAndProcessWidget(parent=self.graph_card)
        self.graph_card.set_content_widget(self.wide_graph)
        bottom_row.addWidget(self.graph_card, stretch=52)

        root_layout.addLayout(bottom_row, stretch=4)

        # 4. 하단 풋터 바 (단축키 안내 및 시스템 요약)
        footer = QLabel(" [F11] FULLSCREEN TOGGLE  |  [M] SWITCH MONITOR  |  [ESC / Q] EXIT HUD  |  HEXAGON MATRIX ACTIVE  |  144Hz DISPLAY READY")
        footer.setFont(get_font_mono(8))
        footer.setStyleSheet(f"color: {HUDColor.TEXT_MUTED.name()}; padding: 1px 8px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root_layout.addWidget(footer)

    def _setup_monitor(self):
        """HDMI-A-1 모니터 타겟팅 및 전체화면"""
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
        sys_meta = data['system']

        # 1. 헤더 업데이트
        self.header_bar.set_uptime(sys_meta['uptime_str'])

        # 2. CPU 타이탄 다이얼 (과열 80도 이상 시 카드 테두리 경고)
        cpu_temp = cpu['temp_c']
        self.cpu_dial.set_values(
            cpu['total_percent'], cpu_temp,
            sub_label="COOLER", sub_val=f"{cpu['fan_rpm']} RPM"
        )
        self.cpu_dial_card.set_critical(cpu_temp >= 80)

        # 3. GPU 타이탄 다이얼 (과열 80도 이상 시 카드 테두리 경고)
        gpu_temp = gpu['temp_c']
        self.gpu_dial.set_values(
            gpu['util_percent'], gpu_temp,
            sub_label="CORE", sub_val=f"{gpu['clock_core_mhz']:,} MHz"
        )
        self.gpu_dial_card.set_critical(gpu_temp >= 80)

        # 4. 중앙 파워 & 메모리 클러스터
        self.power_cluster.set_data(gpu, mem, disk, net)

        # 5. 하단 좌측: 9800X3D 실리콘 다이 매트릭스
        self.die_matrix.update_die(cpu['threads_percent'], cpu['threads_freq'])

        # 6. 하단 우측: 와이드 60초 파형 그래프 & 프로세스 센티넬
        self.wide_graph.update_telemetry(cpu['total_percent'], gpu['util_percent'], procs)

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

    dashboard = CyberpunkDashboard(target_monitor="HDMI-A-1")
    dashboard.setObjectName("sys-dash")
    dashboard.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
