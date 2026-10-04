"""
화이트 & 다크 PCB AIDA64 센서 패널 - CPU & 메인보드 섹션 (독립 분리 패널)
- 패널 1: Ryzen 7 9800X3D CPU 독립 프레임
- 패널 2: GIGABYTE B850I AORUS PRO 메인보드 독립 프레임 (실물 사진 + 버스 링크 펄스 + 서멀 센서)
"""

import os
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, ThemeManager, get_font_bold, get_font_regular
from config import get_resource_path
from widgets.pcb_components import CpuSocketBadge, LiquidDropBadge, VrmChipBadge
from widgets.mini_scope import MiniScopeGraph
from widgets.pcb_bar import PCBProgressBar


class PcbCpuSection(QWidget):
    """
    좌측 컬럼: CPU 독립 패널 + 메인보드 독립 패널
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.meter_labels = []
        self._init_ui()
        ThemeManager.register_listener(self.apply_theme)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # ==========================================
        # 1. CPU 전용 독립 패널 (네모칸 1)
        # ==========================================
        self.cpu_frame = QFrame(self)
        self.cpu_frame.setObjectName("cpu_frame")
        cpu_layout = QVBoxLayout(self.cpu_frame)
        cpu_layout.setContentsMargins(18, 14, 18, 14)
        cpu_layout.setSpacing(8)

        # 1-1. 헤더: 실물 CPU 사진 & 부스트 클럭 & 소켓 온도 배지
        top_h = QHBoxLayout()
        top_h.setSpacing(10)

        left_info = QVBoxLayout()
        left_info.setSpacing(5)

        title_h = QHBoxLayout()
        title_h.setSpacing(8)
        title_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        cpu_photo_path = get_resource_path("assets/cpu_photo.png")
        if os.path.exists(cpu_photo_path):
            self.cpu_img_lbl = QLabel()
            pix = QPixmap(cpu_photo_path).scaled(34, 34, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.cpu_img_lbl.setPixmap(pix)
            title_h.addWidget(self.cpu_img_lbl)

        self.cpu_title_lbl = QLabel("Ryzen 7 9800X3D")
        self.cpu_title_lbl.setFont(get_font_bold(17))
        title_h.addWidget(self.cpu_title_lbl)
        title_h.addStretch()
        left_info.addLayout(title_h)

        clk_h = QHBoxLayout()
        self.clk_tag = QLabel("CPU Boost Clock")
        self.clk_tag.setFont(get_font_regular(11))
        self.clk_val = QLabel("5,200 MHz")
        self.clk_val.setFont(get_font_bold(12))
        clk_h.addWidget(self.clk_tag)
        clk_h.addStretch()
        clk_h.addWidget(self.clk_val)
        left_info.addLayout(clk_h)

        self.clk_bar = PCBProgressBar(max_val=5500.0, height=11, parent=self.cpu_frame)
        left_info.addWidget(self.clk_bar)
        top_h.addLayout(left_info, stretch=1)

        right_badge = QVBoxLayout()
        right_badge.setSpacing(2)
        right_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_tag = QLabel("Temperature (°C)")
        self.temp_tag.setFont(get_font_bold(10))
        self.temp_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_badge.addWidget(self.temp_tag)

        self.cpu_badge = CpuSocketBadge(parent=self.cpu_frame)
        right_badge.addWidget(self.cpu_badge)
        top_h.addLayout(right_badge, stretch=0)
        cpu_layout.addLayout(top_h)

        # 1-2. 코어별 8개 오실로스코프 그래프
        util_h = QHBoxLayout()
        self.util_tag = QLabel("CPU Utilization (Per-Core)")
        self.util_tag.setFont(get_font_regular(11))
        self.util_total_lbl = QLabel("Total 5%")
        self.util_total_lbl.setFont(get_font_bold(12))
        util_h.addWidget(self.util_tag)
        util_h.addStretch()
        util_h.addWidget(self.util_total_lbl)
        cpu_layout.addLayout(util_h)

        cores_layout = QHBoxLayout()
        cores_layout.setSpacing(4)
        self.core_scopes = []
        for i in range(8):
            scope = MiniScopeGraph(max_points=24, show_labels=(i == 0 or i == 7), parent=self.cpu_frame)
            scope.setFixedHeight(98)
            self.core_scopes.append(scope)
            cores_layout.addWidget(scope)
        cpu_layout.addLayout(cores_layout)

        # 1-3. 전압, 전력, 3D V-Cache 바 게이지
        def add_meter_row(label_text, default_val_str, max_v):
            h_box = QHBoxLayout()
            tag = QLabel(label_text)
            tag.setFont(get_font_regular(10))
            val = QLabel(default_val_str)
            val.setFont(get_font_bold(11))
            h_box.addWidget(tag)
            h_box.addStretch()
            h_box.addWidget(val)
            cpu_layout.addLayout(h_box)

            bar = PCBProgressBar(max_val=max_v, height=10, parent=self.cpu_frame)
            cpu_layout.addWidget(bar)
            self.meter_labels.append((tag, val))
            return val, bar

        self.volt_val, self.volt_bar = add_meter_row("Core Voltage", "1.150 V", 1.50)
        self.pwr_val, self.pwr_bar = add_meter_row("CPU Package Power", "38.50 W", 140.0)
        self.cache_val, self.cache_bar = add_meter_row("3D V-Cache (96MB L3)", "96 MB ALLOCATED (OPTIMAL)", 100.0)
        self.cache_bar.set_value(100.0)

        # 1-4. CPU 온도 추이 그래프
        self.temp_trend_lbl = QLabel("CPU Temperature Trend (60s)")
        self.temp_trend_lbl.setFont(get_font_regular(10))
        cpu_layout.addWidget(self.temp_trend_lbl)

        self.temp_scope = MiniScopeGraph(max_points=36, show_labels=False, parent=self.cpu_frame)
        self.temp_scope.setFixedHeight(48)
        cpu_layout.addWidget(self.temp_scope)

        main_layout.addWidget(self.cpu_frame, stretch=6)

        # ==========================================
        # 2. 메인보드 전용 독립 패널 (네모칸 2)
        # ==========================================
        self.mobo_frame = QFrame(self)
        self.mobo_frame.setObjectName("mobo_frame")
        mobo_layout = QVBoxLayout(self.mobo_frame)
        mobo_layout.setContentsMargins(18, 12, 18, 12)
        mobo_layout.setSpacing(8)

        # 2-1. 메인보드 헤더: 실물 사진 에셋 + 타이틀 + 버스 링크 펄스
        mobo_title_h = QHBoxLayout()
        mobo_title_h.setSpacing(8)
        mobo_title_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        mobo_photo_path = get_resource_path("assets/mobo_photo.png")
        self.mobo_img_lbl = QLabel()
        if os.path.exists(mobo_photo_path):
            pix_mobo = QPixmap(mobo_photo_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.mobo_img_lbl.setPixmap(pix_mobo)
        mobo_title_h.addWidget(self.mobo_img_lbl)

        mobo_texts = QVBoxLayout()
        mobo_texts.setSpacing(2)
        self.mobo_title_lbl = QLabel("GIGABYTE B850I AORUS PRO")
        self.mobo_title_lbl.setFont(get_font_bold(14))
        self.mobo_sub_lbl = QLabel("BIOS: F13c  |  PCIe 5.0 x16 Link  |  AMD B850 ITX")
        self.mobo_sub_lbl.setFont(get_font_regular(10))
        mobo_texts.addWidget(self.mobo_title_lbl)
        mobo_texts.addWidget(self.mobo_sub_lbl)
        mobo_title_h.addLayout(mobo_texts)

        mobo_title_h.addStretch()

        # 우측 PCIe 버스 링크 펄스 위젯
        self.bus_link_widget = QWidget()
        self.bus_link_widget.setFixedSize(70, 32)
        self.bus_phase = 0.0
        self.bus_timer = QTimer(self)
        self.bus_timer.timeout.connect(self._bus_tick)
        self.bus_timer.start(40)
        self.bus_link_widget.paintEvent = self._paint_bus_link
        mobo_title_h.addWidget(self.bus_link_widget)

        mobo_layout.addLayout(mobo_title_h)

        # 2-2. 메인보드 서멀 센서 3종
        thermal_h = QHBoxLayout()
        thermal_h.setSpacing(24)
        thermal_h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 수온
        drop_col = QVBoxLayout()
        drop_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_tag = QLabel("Liquid Temp")
        self.drop_tag.setFont(get_font_regular(10))
        self.liquid_badge = LiquidDropBadge(parent=self.mobo_frame)
        drop_col.addWidget(self.drop_tag, alignment=Qt.AlignmentFlag.AlignCenter)
        drop_col.addWidget(self.liquid_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        thermal_h.addLayout(drop_col)

        # VRM 전원부 온도
        vrm_col = QVBoxLayout()
        vrm_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vrm_tag = QLabel("VRM Temp")
        self.vrm_tag.setFont(get_font_regular(10))
        self.vrm_badge = VrmChipBadge(parent=self.mobo_frame)
        vrm_col.addWidget(self.vrm_tag, alignment=Qt.AlignmentFlag.AlignCenter)
        vrm_col.addWidget(self.vrm_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        thermal_h.addLayout(vrm_col)

        # PCH 칩셋 온도
        pch_col = QVBoxLayout()
        pch_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pch_tag = QLabel("PCH Temp")
        self.pch_tag.setFont(get_font_regular(10))
        self.pch_badge = VrmChipBadge(parent=self.mobo_frame)
        pch_col.addWidget(self.pch_tag, alignment=Qt.AlignmentFlag.AlignCenter)
        pch_col.addWidget(self.pch_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        thermal_h.addLayout(pch_col)

        mobo_layout.addLayout(thermal_h)
        main_layout.addWidget(self.mobo_frame, stretch=4)

        self.apply_theme()

    def _bus_tick(self):
        self.bus_phase = (self.bus_phase + 0.08) % (math.pi * 2)
        self.bus_link_widget.update()

    def _paint_bus_link(self, event):
        painter = QPainter(self.bus_link_widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        is_dark = ThemeManager.is_dark()
        w = float(self.bus_link_widget.width())

        # 4개의 데이터 링크 LED
        for i in range(4):
            px = 10.0 + i * 14.0
            py = 10.0
            shift = (self.bus_phase - i * 0.8) % (math.pi * 2)
            intensity = (math.sin(shift) + 1.0) / 2.0
            led_c = QColor(0, int(180 + 75 * intensity), int(220 + 35 * intensity)) if is_dark else QColor(int(200 + 55 * intensity), 80, 0)
            painter.setBrush(QBrush(led_c))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), 2.5, 2.5)

        painter.setFont(get_font_bold(8))
        link_c = QColor(0, 220, 255) if is_dark else QColor(255, 110, 0)
        painter.setPen(QPen(link_c))
        painter.drawText(QRectF(0, 16, w, 14), Qt.AlignmentFlag.AlignCenter, "LINK ACTIVE")

    def apply_theme(self):
        c_bg = WhitePCBColor.BG_PANEL.name()
        c_border = WhitePCBColor.BORDER_MAIN.name()
        c_main = WhitePCBColor.TEXT_MAIN.name()
        c_sub = WhitePCBColor.TEXT_SUB.name()
        c_muted = WhitePCBColor.TEXT_MUTED.name()

        frame_style = f"background-color: {c_bg}; border: 2.5px solid {c_border};"
        self.cpu_frame.setStyleSheet(f"#cpu_frame {{ {frame_style} }}")
        self.mobo_frame.setStyleSheet(f"#mobo_frame {{ {frame_style} }}")

        self.cpu_title_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.clk_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.clk_val.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.temp_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.util_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.util_total_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.temp_trend_lbl.setStyleSheet(f"color: {c_sub}; margin-top: 2px; border: none; background: transparent;")

        for tag, val in self.meter_labels:
            tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
            val.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")

        self.mobo_title_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.mobo_sub_lbl.setStyleSheet(f"color: {c_muted}; border: none; background: transparent;")

        self.drop_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.vrm_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.pch_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")

        self.update()

    def update_data(self, cpu_data, mobo_data=None):
        if mobo_data:
            vendor = mobo_data.get("vendor", "GIGABYTE")
            board = mobo_data.get("board_name", "B850I AORUS PRO")
            bios = mobo_data.get("bios_ver", "F13c")
            chipset = mobo_data.get("chipset", "AMD B850")
            self.mobo_title_lbl.setText(f"{vendor} {board}")
            self.mobo_sub_lbl.setText(f"BIOS: {bios}  |  PCIe 5.0 x16 Link  |  {chipset} ITX")

        temp = cpu_data.get('temp_c', 45.0)
        self.cpu_badge.set_temp(temp)
        self.liquid_badge.set_temp(max(28, int(temp * 0.72)))
        self.vrm_badge.set_temp(int(temp + 2))
        self.pch_badge.set_temp(int(temp - 3))
        self.temp_scope.add_point(temp)

        tot_pct = cpu_data.get('total_percent', 0.0)
        self.util_total_lbl.setText(f"Total {int(round(tot_pct))}%")

        freqs = cpu_data.get('threads_freq', [])
        max_f = max(freqs) if freqs else 0
        self.clk_val.setText(f"{max_f:,} MHz")
        self.clk_bar.set_value(max_f)

        threads_pct = cpu_data.get('threads_percent', [])
        for i in range(8):
            t_idx = i * 2
            p = threads_pct[t_idx] if t_idx < len(threads_pct) else 0.0
            self.core_scopes[i].add_point(p)

        est_pwr = 28.0 + (tot_pct * 0.8)
        self.pwr_val.setText(f"{est_pwr:.2f} W")
        self.pwr_bar.set_value(est_pwr)
        self.volt_val.setText("1.125 V")
        self.volt_bar.set_value(1.125)
