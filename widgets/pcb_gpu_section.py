"""
화이트 & 다크 PCB AIDA64 센서 패널 - GPU & 네트워크 & 프로세스 섹션 (독립 분리 패널)
- 패널 1: GeForce RTX 5070 Ti 독립 프레임
- 패널 2: Network Sentinel (Wi-Fi 6E) 독립 프레임 (실물 사진 + 듀얼 오실로스코프 + 패킷 스트림)
- 패널 3: TOP 5 RESOURCE SENTINEL 프로세스 독립 프레임
"""

import os
import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPixmap
from PyQt6.QtCore import Qt, QRectF, QTimer
from theme import WhitePCBColor, ThemeManager, get_font_bold, get_font_regular
from config import get_resource_path
from widgets.pcb_components import GpuCardBadge
from widgets.mini_scope import MiniScopeGraph
from widgets.pcb_bar import PCBProgressBar
from widgets.process_table import TopProcessTable
from hardware_detector import HardwareDetector


class MonitorFpsCard(QFrame):
    """
    단일 모니터 실시간 실황 FPS 카드 위젯
    """
    def __init__(self, default_port, default_hz, parent=None):
        super().__init__(parent)
        self.port_name = default_port
        self.max_hz = default_hz
        self.is_focused = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(1)

        # 상단 헤더: 포트 및 주사율
        header_h = QHBoxLayout()
        header_h.setSpacing(4)
        self.title_lbl = QLabel(f"{self.port_name} ({self.max_hz}Hz)")
        self.title_lbl.setFont(get_font_bold(8))
        header_h.addWidget(self.title_lbl)
        header_h.addStretch()

        self.focus_lbl = QLabel("●")
        self.focus_lbl.setFont(get_font_bold(7))
        header_h.addWidget(self.focus_lbl)
        layout.addLayout(header_h)

        # 중앙: 대형 실황 FPS 수치
        self.fps_lbl = QLabel(f"{self.max_hz} FPS")
        self.fps_lbl.setFont(get_font_bold(13))
        self.fps_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.fps_lbl)

        # 하단: 액티비티 태그 (YOUTUBE / GAME / DESKTOP)
        self.act_lbl = QLabel("DESKTOP")
        self.act_lbl.setFont(get_font_bold(7))
        self.act_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.act_lbl)

    def update_info(self, name, model, max_hz, current_fps, activity, focused):
        self.port_name = name
        self.max_hz = max_hz
        self.is_focused = focused

        short_model = model.split()[0] if model else ""
        if short_model:
            self.title_lbl.setText(f"{name} {short_model} ({max_hz}Hz)")
        else:
            self.title_lbl.setText(f"{name} ({max_hz}Hz)")

        self.fps_lbl.setText(f"{current_fps} FPS")

        if activity == "YOUTUBE":
            self.act_lbl.setText("● YOUTUBE")
        elif activity == "GAME":
            self.act_lbl.setText("● GAME ACTIVE")
        elif activity == "VIDEO":
            self.act_lbl.setText("● MEDIA PLAY")
        elif activity == "SENSOR HUD":
            self.act_lbl.setText("● SENSOR HUD")
        else:
            self.act_lbl.setText("DESKTOP")

        self.apply_style()

    def apply_style(self):
        is_dark = ThemeManager.is_dark()
        if self.is_focused:
            border_c = "#00d2ff" if is_dark else "#ff6600"
            bg_c = "rgba(0, 180, 255, 0.09)" if is_dark else "rgba(255, 102, 0, 0.07)"
            focus_c = "#00ffcc" if is_dark else "#ff5500"
        else:
            border_c = "#262e3e" if is_dark else "#d0d6e2"
            bg_c = "#141722" if is_dark else "#f3f5f8"
            focus_c = "#40485c" if is_dark else "#9aa0b0"

        self.setStyleSheet(f"""
            MonitorFpsCard {{
                background-color: {bg_c};
                border: 1.5px solid {border_c};
                border-radius: 4px;
            }}
        """)

        title_c = "#a0aec0" if is_dark else "#4a5568"
        self.title_lbl.setStyleSheet(f"color: {title_c}; border: none; background: transparent;")
        self.focus_lbl.setStyleSheet(f"color: {focus_c}; border: none; background: transparent;")

        fps_c = "#00f0ff" if is_dark else "#d95500"
        self.fps_lbl.setStyleSheet(f"color: {fps_c}; border: none; background: transparent;")

        act_text = self.act_lbl.text()
        if "YOUTUBE" in act_text:
            act_c = "#ff4444" if is_dark else "#cc1111"
        elif "GAME" in act_text:
            act_c = "#ffaa00" if is_dark else "#d97706"
        elif "SENSOR" in act_text:
            act_c = "#00e676" if is_dark else "#059669"
        else:
            act_c = "#718096" if is_dark else "#718096"
        self.act_lbl.setStyleSheet(f"color: {act_c}; border: none; background: transparent;")


class TripleMonitorFpsWidget(QWidget):
    """
    3개 모니터 실시간 실황 FPS HUD 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.card_main = MonitorFpsCard("DP-3", 100, parent=self)
        self.card_sub = MonitorFpsCard("DP-2", 60, parent=self)
        self.card_hud = MonitorFpsCard("HDMI-1", 144, parent=self)

        layout.addWidget(self.card_main)
        layout.addWidget(self.card_sub)
        layout.addWidget(self.card_hud)

        self.apply_theme()

    def apply_theme(self):
        self.card_main.apply_style()
        self.card_sub.apply_style()
        self.card_hud.apply_style()

    def update_monitors(self, monitors_data):
        if not monitors_data:
            return
        mons = monitors_data.get("monitors", [])
        cards = [self.card_main, self.card_sub, self.card_hud]
        for idx, m in enumerate(mons[:3]):
            name = m.get("name", "")
            model = m.get("model", "")
            hz = m.get("max_hz", 60)
            fps = m.get("current_fps", hz)
            act = m.get("activity", "DESKTOP")
            foc = m.get("focused", False)
            cards[idx].update_info(name, model, hz, fps, act, foc)


class PcbGpuSection(QWidget):
    """
    우측 컬럼: GPU 독립 패널 + 네트워크 독립 패널 + 프로세스 독립 패널
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
        # 1. GPU 전용 독립 패널 (네모칸 1)
        # ==========================================
        self.gpu_frame = QFrame(self)
        self.gpu_frame.setObjectName("gpu_frame")
        gpu_layout = QVBoxLayout(self.gpu_frame)
        gpu_layout.setContentsMargins(18, 14, 18, 14)
        gpu_layout.setSpacing(8)

        # 1-1. 헤더: 실물 GPU 사진 & 클럭 & 그래픽카드 배지
        top_h = QHBoxLayout()
        top_h.setSpacing(10)

        left_info = QVBoxLayout()
        left_info.setSpacing(5)

        title_h = QHBoxLayout()
        title_h.setSpacing(8)
        title_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        gpu_photo_path = get_resource_path("assets/gpu_photo.png")
        if os.path.exists(gpu_photo_path):
            self.gpu_img_lbl = QLabel()
            pix_gpu = QPixmap(gpu_photo_path).scaled(92, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.gpu_img_lbl.setPixmap(pix_gpu)
            title_h.addWidget(self.gpu_img_lbl)

        hw_gpu = HardwareDetector.get_gpu_info()
        hw_router = HardwareDetector.get_router_info()

        self.gpu_title_lbl = QLabel(hw_gpu["model"])
        self.gpu_title_lbl.setFont(get_font_bold(17))
        title_h.addWidget(self.gpu_title_lbl)
        title_h.addStretch()
        left_info.addLayout(title_h)

        clk_h = QHBoxLayout()
        self.clk_tag = QLabel("GPU Core Clock")
        self.clk_tag.setFont(get_font_regular(11))
        self.clk_val = QLabel(f"{int(hw_gpu['max_clock_mhz']):,} MHz")
        self.clk_val.setFont(get_font_bold(12))
        clk_h.addWidget(self.clk_tag)
        clk_h.addStretch()
        clk_h.addWidget(self.clk_val)
        left_info.addLayout(clk_h)

        self.clk_bar = PCBProgressBar(max_val=max(3000.0, hw_gpu["max_clock_mhz"] + 200), height=11, parent=self.gpu_frame)
        left_info.addWidget(self.clk_bar)
        top_h.addLayout(left_info, stretch=1)

        right_badge = QVBoxLayout()
        right_badge.setSpacing(2)
        right_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_tag = QLabel("Temperature (°C)")
        self.temp_tag.setFont(get_font_bold(10))
        self.temp_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_badge.addWidget(self.temp_tag)

        self.gpu_badge = GpuCardBadge(parent=self.gpu_frame)
        right_badge.addWidget(self.gpu_badge)
        top_h.addLayout(right_badge, stretch=0)
        gpu_layout.addLayout(top_h)

        # 1-2. 3대 모니터 실시간 실황 FPS 센티넬 바 (Triple Monitor Realtime FPS Sentinel)
        self.monitors_fps_widget = TripleMonitorFpsWidget(parent=self.gpu_frame)
        gpu_layout.addWidget(self.monitors_fps_widget)

        # 1-3. GPU Utl & FPS 듀얼 오실로스코프 그래프
        graph_labels_h = QHBoxLayout()
        self.utl_lbl = QLabel("GPU Utl   10%")
        self.utl_lbl.setFont(get_font_bold(11))
        graph_labels_h.addWidget(self.utl_lbl, stretch=1)

        self.fps_lbl = QLabel("FPS (MAIN DP-3)   60 FPS")
        self.fps_lbl.setFont(get_font_bold(11))
        graph_labels_h.addWidget(self.fps_lbl, stretch=1)
        gpu_layout.addLayout(graph_labels_h)

        graphs_h = QHBoxLayout()
        graphs_h.setSpacing(8)
        self.utl_scope = MiniScopeGraph(max_points=32, show_labels=True, parent=self.gpu_frame)
        self.utl_scope.setFixedHeight(84)
        self.fps_scope = MiniScopeGraph(max_points=32, show_labels=True, parent=self.gpu_frame)
        self.fps_scope.setFixedHeight(84)
        graphs_h.addWidget(self.utl_scope)
        graphs_h.addWidget(self.fps_scope)
        gpu_layout.addLayout(graphs_h)

        # 1-3. VRAM, 클럭, 전압, 전력 바 게이지
        def add_meter_row(label_text, default_val_str, max_v):
            h_box = QHBoxLayout()
            tag = QLabel(label_text)
            tag.setFont(get_font_regular(10))
            val = QLabel(default_val_str)
            val.setFont(get_font_bold(11))
            h_box.addWidget(tag)
            h_box.addStretch()
            h_box.addWidget(val)
            gpu_layout.addLayout(h_box)

            bar = PCBProgressBar(max_val=max_v, height=10, parent=self.gpu_frame)
            gpu_layout.addWidget(bar)
            self.meter_labels.append((tag, val))
            return tag, val, bar

        self.vram_tag, self.vram_val, self.vram_bar = add_meter_row(hw_gpu["vram_label"], "1,640 MB (10.2%)", 100.0)
        self.mem_clk_tag, self.mem_clk_val, self.mem_clk_bar = add_meter_row("GDDR7 Memory Clock", "14,001 MHz", 16000.0)
        self.mem_clk_bar.set_value(14001.0)
        self.volt_tag, self.volt_val, self.volt_bar = add_meter_row("Core Voltage", "0.850 V", 1.20)
        self.pwr_tag, self.pwr_val, self.pwr_bar = add_meter_row("Package Power (TGP)", "38.10 W | 13%", hw_gpu["tgp_w"])

        main_layout.addWidget(self.gpu_frame, stretch=6)

        # ==========================================
        # 2. 네트워크 센티넬 전용 독립 패널 (네모칸 2)
        # ==========================================
        self.net_frame = QFrame(self)
        self.net_frame.setObjectName("net_frame")
        net_layout = QVBoxLayout(self.net_frame)
        net_layout.setContentsMargins(16, 10, 16, 10)
        net_layout.setSpacing(6)

        # 네트워크 헤더 (실물 사진 에셋 + 타이틀 + 대역폭 수치)
        net_title_h = QHBoxLayout()
        net_title_h.setSpacing(8)
        net_title_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        net_photo_path = get_resource_path("assets/net_photo.png")
        self.net_img_lbl = QLabel()
        if os.path.exists(net_photo_path):
            pix_net = QPixmap(net_photo_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.net_img_lbl.setPixmap(pix_net)
        net_title_h.addWidget(self.net_img_lbl)

        net_texts = QVBoxLayout()
        net_texts.setSpacing(2)
        self.net_title_lbl = QLabel(hw_router)
        self.net_title_lbl.setFont(get_font_bold(13))
        self.net_sub_lbl = QLabel("wlp8s0  |  IP: 192.168.50.206")
        self.net_sub_lbl.setFont(get_font_regular(10))
        net_texts.addWidget(self.net_title_lbl)
        net_texts.addWidget(self.net_sub_lbl)
        net_title_h.addLayout(net_texts)

        net_title_h.addStretch()

        self.net_rate_lbl = QLabel("▼ 0.0 MB/s   ▲ 0.0 MB/s")
        self.net_rate_lbl.setFont(get_font_bold(11))
        net_title_h.addWidget(self.net_rate_lbl)

        net_layout.addLayout(net_title_h)

        # 실시간 다운/업로드 듀얼 미니 오실로스코프 그래프
        net_scopes_h = QHBoxLayout()
        net_scopes_h.setSpacing(8)

        self.down_scope = MiniScopeGraph(max_points=28, show_labels=False, parent=self.net_frame)
        self.down_scope.setFixedHeight(46)
        net_scopes_h.addWidget(self.down_scope)

        self.up_scope = MiniScopeGraph(max_points=28, show_labels=False, parent=self.net_frame)
        self.up_scope.setFixedHeight(46)
        net_scopes_h.addWidget(self.up_scope)

        net_layout.addLayout(net_scopes_h)
        main_layout.addWidget(self.net_frame, stretch=2)

        # ==========================================
        # 3. 상위 프로세스 HUD 센티넬 독립 패널 (네모칸 3)
        # ==========================================
        self.proc_frame = QFrame(self)
        self.proc_frame.setObjectName("proc_frame")
        proc_layout = QVBoxLayout(self.proc_frame)
        proc_layout.setContentsMargins(16, 8, 16, 8)
        proc_layout.setSpacing(4)

        self.proc_title = QLabel("TOP 5 RESOURCE SENTINEL (ACTIVE TASKS)")
        self.proc_title.setFont(get_font_bold(10))
        proc_layout.addWidget(self.proc_title)

        self.proc_table = TopProcessTable(parent=self.proc_frame)
        self.proc_table.setFixedHeight(116)
        proc_layout.addWidget(self.proc_table)

        main_layout.addWidget(self.proc_frame, stretch=3)

        self.apply_theme()

    def apply_theme(self):
        c_bg = WhitePCBColor.BG_PANEL.name()
        c_border = WhitePCBColor.BORDER_MAIN.name()
        c_main = WhitePCBColor.TEXT_MAIN.name()
        c_sub = WhitePCBColor.TEXT_SUB.name()
        c_muted = WhitePCBColor.TEXT_MUTED.name()

        frame_style = f"background-color: {c_bg}; border: 2.5px solid {c_border};"
        self.gpu_frame.setStyleSheet(f"#gpu_frame {{ {frame_style} }}")
        self.net_frame.setStyleSheet(f"#net_frame {{ {frame_style} }}")
        self.proc_frame.setStyleSheet(f"#proc_frame {{ {frame_style} }}")

        self.gpu_title_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.clk_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.clk_val.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.temp_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.utl_lbl.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.fps_lbl.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")

        for tag, val in self.meter_labels:
            tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
            val.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")

        self.net_title_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.net_sub_lbl.setStyleSheet(f"color: {c_muted}; border: none; background: transparent;")
        self.net_rate_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.proc_title.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")

        if hasattr(self, 'monitors_fps_widget'):
            self.monitors_fps_widget.apply_theme()

        self.update()

    def update_data(self, gpu_data, procs, net_data=None):
        # GPU 모델명 및 VRAM 라벨 동적 갱신
        gpu_model = gpu_data.get("model")
        if gpu_model and self.gpu_title_lbl.text() != gpu_model:
            self.gpu_title_lbl.setText(gpu_model)

        vram_label = gpu_data.get("vram_label")
        if vram_label and self.vram_tag.text() != vram_label:
            self.vram_tag.setText(vram_label)

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

        # 3대 모니터 실시간 실황 FPS 및 액티비티 갱신
        monitors_data = gpu_data.get('monitors_fps', {})
        self.monitors_fps_widget.update_monitors(monitors_data)

        active_fps = monitors_data.get('active_fps', 60)
        active_label = monitors_data.get('active_label', 'MAIN')
        self.fps_lbl.setText(f"FPS ({active_label})   {active_fps} FPS")
        self.fps_scope.add_point(min(100.0, (active_fps / 144.0) * 100.0))

        # VRAM
        v_used = int(gpu_data.get('vram_used_mb', 0))
        pct_v = gpu_data.get('vram_percent', 0)
        self.vram_val.setText(f"{v_used:,} MB ({pct_v:.1f}%)")
        self.vram_bar.set_value(pct_v)

        # Power
        pwr = gpu_data.get('power_w', 0.0)
        limit = gpu_data.get('power_limit_w', 300.0)
        self.pwr_bar.max_val = limit
        pct = (pwr / limit) * 100.0 if limit > 0 else 0
        self.pwr_val.setText(f"{pwr:.1f} W | {int(round(pct))}%")
        self.pwr_bar.set_value(pwr)

        self.volt_val.setText("0.850 V")
        self.volt_bar.set_value(0.850)

        # 네트워크 모듈 갱신
        if net_data:
            router = net_data.get("router_model")
            if router and self.net_title_lbl.text() != router:
                self.net_title_lbl.setText(router)
            iface = net_data.get("iface", "wlp8s0")
            ip = net_data.get("ip", "192.168.50.206")
            down_mb = net_data.get("down_mb_s", 0.0)
            up_mb = net_data.get("up_mb_s", 0.0)
            self.net_sub_lbl.setText(f"{iface}  |  IP: {ip}")
            self.net_rate_lbl.setText(f"▼ {down_mb:.1f} MB/s   ▲ {up_mb:.1f} MB/s")
            self.down_scope.add_point(min(100.0, down_mb * 10.0))
            self.up_scope.add_point(min(100.0, up_mb * 20.0))

        self.proc_table.set_processes(procs)
