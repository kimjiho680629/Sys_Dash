"""
화이트 PCB AIDA64 센서 패널 - GPU 섹션 (화면 꽉 찬 고밀도 튜닝)
GeForce RTX 5070 Ti, 대형 GPU/FPS 오실로스코프, GPU 카드 배지, 메모리 클럭, 팬, 프로세스 테이블
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from theme import WhitePCBColor, get_font_bold, get_font_regular
from widgets.pcb_components import GpuCardBadge
from widgets.mini_scope import MiniScopeGraph
from widgets.pcb_bar import PCBProgressBar
from widgets.process_table import TopProcessTable


class PcbGpuSection(QWidget):
    """
    화이트 PCB 센서패널 GPU 섹션 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(10)

        # 1. 헤더: GeForce RTX 5070 Ti & Temperature (°C)
        top_h = QHBoxLayout()
        top_h.setSpacing(10)

        left_info = QVBoxLayout()
        left_info.setSpacing(6)

        title_lbl = QLabel("GeForce RTX 5070 Ti")
        title_lbl.setFont(get_font_bold(20))
        title_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()};")
        left_info.addWidget(title_lbl)

        # GPU Clock 라벨 및 수치
        clk_h = QHBoxLayout()
        clk_tag = QLabel("GPU Core Clock")
        clk_tag.setFont(get_font_bold(10))
        clk_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        self.clk_val = QLabel("2,550 MHz")
        self.clk_val.setFont(get_font_bold(10))
        self.clk_val.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()};")
        clk_h.addWidget(clk_tag)
        clk_h.addStretch()
        clk_h.addWidget(self.clk_val)
        left_info.addLayout(clk_h)

        self.clk_bar = PCBProgressBar(max_val=3000.0, height=14, parent=self)
        left_info.addWidget(self.clk_bar)

        top_h.addLayout(left_info, stretch=1)

        # 우측: 그래픽카드 온도 배지
        right_badge = QVBoxLayout()
        right_badge.setSpacing(2)
        right_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        temp_tag = QLabel("Temperature (°C)")
        temp_tag.setFont(get_font_bold(8))
        temp_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        temp_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_badge.addWidget(temp_tag)

        self.gpu_badge = GpuCardBadge(parent=self)
        right_badge.addWidget(self.gpu_badge)
        top_h.addLayout(right_badge, stretch=0)

        main_layout.addLayout(top_h)

        # 2. GPU Utilization & FPS 듀얼 대형 오실로스코프 그래프 (120px)
        graph_labels_h = QHBoxLayout()
        
        self.utl_lbl = QLabel("GPU Utl   10%")
        self.utl_lbl.setFont(get_font_bold(10))
        self.utl_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        graph_labels_h.addWidget(self.utl_lbl, stretch=1)

        self.fps_lbl = QLabel("FPS   144 FPS")
        self.fps_lbl.setFont(get_font_bold(10))
        self.fps_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        graph_labels_h.addWidget(self.fps_lbl, stretch=1)
        main_layout.addLayout(graph_labels_h)

        graphs_h = QHBoxLayout()
        graphs_h.setSpacing(10)
        self.utl_scope = MiniScopeGraph(max_points=32, show_labels=True, parent=self)
        self.utl_scope.setFixedHeight(120)
        self.fps_scope = MiniScopeGraph(max_points=32, show_labels=True, parent=self)
        self.fps_scope.setFixedHeight(120)
        graphs_h.addWidget(self.utl_scope)
        graphs_h.addWidget(self.fps_scope)
        main_layout.addLayout(graphs_h)

        # 3. VRAM, Memory Clock, Voltage, Power 바 게이지들
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

        self.vram_val, self.vram_bar = add_meter_row("VRAM (GDDR7 16GB)", "1,640 MB (10.2%)", 100.0)
        self.mem_clk_val, self.mem_clk_bar = add_meter_row("GDDR7 Memory Clock", "14,001 MHz", 16000.0)
        self.mem_clk_bar.set_value(14001.0)
        self.volt_val, self.volt_bar = add_meter_row("Core Voltage", "0.850 V", 1.20)
        self.pwr_val, self.pwr_bar = add_meter_row("Package Power (TGP)", "38.10 W | 13%", 300.0)

        # 구분선
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {WhitePCBColor.BORDER_LIGHT.name()};")
        main_layout.addWidget(sep)

        # 4. 하단: 상위 프로세스 HUD 센티넬 테이블 (160px 대형화)
        proc_title = QLabel("TOP 5 RESOURCE SENTINEL (ACTIVE TASKS)")
        proc_title.setFont(get_font_bold(9))
        proc_title.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()};")
        main_layout.addWidget(proc_title)

        self.proc_table = TopProcessTable(parent=self)
        self.proc_table.setFixedHeight(160)
        main_layout.addWidget(self.proc_table)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        painter.setBrush(QBrush(WhitePCBColor.BG_PANEL))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 2.5))
        painter.drawRect(QRectF(1, 1, w - 2, h - 2))

    def update_data(self, gpu_data, procs):
        temp = gpu_data.get('temp_c', 35)
        self.gpu_badge.set_temp(temp)

        core_clk = gpu_data.get('clock_core_mhz', 0)
        self.clk_val.setText(f"{core_clk:,} MHz")
        self.clk_bar.set_value(core_clk)

        mem_clk = gpu_data.get('clock_mem_mhz', 14001)
        self.mem_clk_val.setText(f"{mem_clk:,} MHz")
        self.mem_clk_bar.set_value(mem_clk)

        gpu_util = gpu_data.get('util_percent', 0)
        self.utl_lbl.setText(f"GPU Utl   {gpu_util}%")
        self.utl_scope.add_point(gpu_util)

        fps_val = 144 if gpu_util > 5 else 60
        self.fps_lbl.setText(f"FPS   {fps_val} FPS")
        self.fps_scope.add_point(fps_val / 1.44)

        # VRAM
        v_used = int(gpu_data.get('vram_used_mb', 0))
        pct_v = gpu_data.get('vram_percent', 0)
        self.vram_val.setText(f"{v_used:,} MB ({pct_v:.1f}%)")
        self.vram_bar.set_value(pct_v)

        # Power
        pwr = gpu_data.get('power_w', 0.0)
        limit = gpu_data.get('power_limit_w', 300.0)
        pct = (pwr / limit) * 100.0 if limit > 0 else 0
        self.pwr_val.setText(f"{pwr:.1f} W | {int(round(pct))}%")
        self.pwr_bar.set_value(pwr)

        self.volt_val.setText("0.850 V")
        self.volt_bar.set_value(0.850)

        self.proc_table.set_processes(procs)
