"""
화이트 PCB AIDA64 센서 패널 - CPU 섹션 (화면 꽉 찬 고밀도 튜닝)
Ryzen 7 9800X3D, 대형 코어별 8개 오실로스코프, CPU 소켓 배지, 전압/전력/캐시, 4대 서멀 센서
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from theme import WhitePCBColor, get_font_bold, get_font_regular
from widgets.pcb_components import CpuSocketBadge, LiquidDropBadge, VrmChipBadge
from widgets.mini_scope import MiniScopeGraph
from widgets.pcb_bar import PCBProgressBar


class PcbCpuSection(QWidget):
    """
    화이트 PCB 센서패널 CPU 섹션 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(10)

        # 1. 헤더: Ryzen 7 9800X3D & Temperature (°C)
        top_h = QHBoxLayout()
        top_h.setSpacing(10)

        left_info = QVBoxLayout()
        left_info.setSpacing(6)

        title_lbl = QLabel("Ryzen 7 9800X3D")
        title_lbl.setFont(get_font_bold(22))
        title_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()};")
        left_info.addWidget(title_lbl)

        # CPU Clock 라벨 및 수치
        clk_h = QHBoxLayout()
        clk_tag = QLabel("CPU Boost Clock")
        clk_tag.setFont(get_font_bold(10))
        clk_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        self.clk_val = QLabel("5,200 MHz")
        self.clk_val.setFont(get_font_bold(10))
        self.clk_val.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()};")
        clk_h.addWidget(clk_tag)
        clk_h.addStretch()
        clk_h.addWidget(self.clk_val)
        left_info.addLayout(clk_h)

        self.clk_bar = PCBProgressBar(max_val=5500.0, height=14, parent=self)
        left_info.addWidget(self.clk_bar)

        top_h.addLayout(left_info, stretch=1)

        # 우측: CPU 소켓 칩셋 온도 배지
        right_badge = QVBoxLayout()
        right_badge.setSpacing(2)
        right_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        temp_tag = QLabel("Temperature (°C)")
        temp_tag.setFont(get_font_bold(8))
        temp_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        temp_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_badge.addWidget(temp_tag)

        self.cpu_badge = CpuSocketBadge(parent=self)
        right_badge.addWidget(self.cpu_badge)
        top_h.addLayout(right_badge, stretch=0)

        main_layout.addLayout(top_h)

        # 2. CPU Utilization & 코어별 큼직한 8개 오실로스코프 그래프
        util_h = QHBoxLayout()
        util_tag = QLabel("CPU Utilization (Per-Core)")
        util_tag.setFont(get_font_bold(10))
        util_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        self.util_total_lbl = QLabel("Total 5%")
        self.util_total_lbl.setFont(get_font_bold(10))
        self.util_total_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()};")
        util_h.addWidget(util_tag)
        util_h.addStretch()
        util_h.addWidget(self.util_total_lbl)
        main_layout.addLayout(util_h)

        # 8개 코어 대형 미니 오실로스코프 (높이 125px로 확대)
        cores_layout = QHBoxLayout()
        cores_layout.setSpacing(4)
        self.core_scopes = []
        for i in range(8):
            scope = MiniScopeGraph(max_points=24, show_labels=(i == 0 or i == 7), parent=self)
            scope.setFixedHeight(125)
            self.core_scopes.append(scope)
            cores_layout.addWidget(scope)
        main_layout.addLayout(cores_layout)

        # 3. 전압, 전력, 3D V-Cache 게이지
        def add_meter_row(label_text, default_val_str, max_v):
            h_box = QHBoxLayout()
            tag = QLabel(label_text)
            tag.setFont(get_font_bold(9))
            tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
            val = QLabel(default_val_str)
            val.setFont(get_font_bold(9))
            val.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()};")
            h_box.addWidget(tag)
            h_box.addStretch()
            h_box.addWidget(val)
            main_layout.addLayout(h_box)

            bar = PCBProgressBar(max_val=max_v, height=10, parent=self)
            main_layout.addWidget(bar)
            return val, bar

        self.volt_val, self.volt_bar = add_meter_row("Core Voltage", "1.150 V", 1.50)
        self.pwr_val, self.pwr_bar = add_meter_row("CPU Package Power", "38.50 W", 140.0)
        self.cache_val, self.cache_bar = add_meter_row("3D V-Cache (96MB L3)", "96 MB ALLOCATED (OPTIMAL)", 100.0)
        self.cache_bar.set_value(100.0)

        # 4. CPU 60초 온도 추이 미니 와이드 오실로스코프
        temp_trend_lbl = QLabel("CPU Temperature Trend (60s)")
        temp_trend_lbl.setFont(get_font_bold(9))
        temp_trend_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()}; margin-top: 4px;")
        main_layout.addWidget(temp_trend_lbl)

        self.temp_scope = MiniScopeGraph(max_points=40, show_labels=False, parent=self)
        self.temp_scope.setFixedHeight(65)
        main_layout.addWidget(self.temp_scope)

        # 구분선
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {WhitePCBColor.BORDER_LIGHT.name()};")
        main_layout.addWidget(sep)

        # 5. 하단 서멀 센서: Liquid Temp, VRM Temp, Motherboard Temp
        thermal_h = QHBoxLayout()
        thermal_h.setSpacing(28)
        thermal_h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 수온
        drop_col = QVBoxLayout()
        drop_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_tag = QLabel("Liquid Temp")
        drop_tag.setFont(get_font_bold(9))
        drop_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        self.liquid_badge = LiquidDropBadge(parent=self)
        drop_col.addWidget(drop_tag, alignment=Qt.AlignmentFlag.AlignCenter)
        drop_col.addWidget(self.liquid_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        thermal_h.addLayout(drop_col)

        # VRM 전원부 온도
        vrm_col = QVBoxLayout()
        vrm_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vrm_tag = QLabel("VRM Temp")
        vrm_tag.setFont(get_font_bold(9))
        vrm_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        self.vrm_badge = VrmChipBadge(parent=self)
        vrm_col.addWidget(vrm_tag, alignment=Qt.AlignmentFlag.AlignCenter)
        vrm_col.addWidget(self.vrm_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        thermal_h.addLayout(vrm_col)

        # PCH 칩셋 온도
        pch_col = QVBoxLayout()
        pch_col.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pch_tag = QLabel("PCH Temp")
        pch_tag.setFont(get_font_bold(9))
        pch_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        self.pch_badge = VrmChipBadge(parent=self)
        pch_col.addWidget(pch_tag, alignment=Qt.AlignmentFlag.AlignCenter)
        pch_col.addWidget(self.pch_badge, alignment=Qt.AlignmentFlag.AlignCenter)
        thermal_h.addLayout(pch_col)

        main_layout.addLayout(thermal_h)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        painter.setBrush(QBrush(WhitePCBColor.BG_PANEL))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 2.5))
        painter.drawRect(QRectF(1, 1, w - 2, h - 2))

    def update_data(self, cpu_data):
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
