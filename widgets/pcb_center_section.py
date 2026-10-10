"""
화이트 & 다크 PCB AIDA64 센서 패널 - 중앙 섹션 (독립 분리 패널)
- 패널 1: XPG LANCER RGB DDR5 64GB 독립 프레임
- 중간: 사선 챔퍼 시계 & 날짜 바
- 패널 2: Samsung 980 Pro SSD 스토리지 & 쿨링 팬 독립 프레임 (실물 사진 전용, SSD 아이콘 배지 삭제)
- 패널 3: PipeWire Master Audio 독립 프레임 (실물 오디오 사진 + 8밴드 점핑 VU 이퀄라이저)
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
)
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPixmap
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, ThemeManager, get_font_bold, get_font_regular
from config import get_resource_path
from widgets.pcb_components import XpgLancerBadge, TridentZBadge, AudioVuVisualizer
from widgets.pcb_bar import PCBProgressBar
from widgets.pcb_panels import ClockLogoBar
from widgets.mini_scope import MiniScopeGraph
from hardware_detector import HardwareDetector


class FanSpinBadge(QWidget):
    """회전하는 쿨링 팬 아이콘"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.fan_angle = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)
        self.timer.start(30)

    def _rotate(self):
        self.fan_angle = (self.fan_angle + 8.0) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        cx, cy = w / 2.0, h / 2.0
        r = min(w, h) / 2.0 - 4.0
        is_dark = ThemeManager.is_dark()

        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.8))
        bg_fan = QColor(25, 29, 40) if is_dark else QColor(45, 48, 58)
        painter.setBrush(QBrush(bg_fan))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.fan_angle)
        blade_c = QColor(0, 220, 255) if is_dark else Qt.GlobalColor.white
        painter.setPen(QPen(blade_c, 1.8))
        for i in range(5):
            painter.rotate(72)
            painter.drawLine(0, 0, 0, int(r - 3))
        painter.restore()


class PcbCenterSection(QWidget):
    """
    중앙 컬럼: RAM 독립 패널 + 시계 바 + 스토리지/쿨링 독립 패널 + 사운드 독립 패널
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spec_labels = []
        self._init_ui()
        ThemeManager.register_listener(self.apply_theme)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # ==========================================
        # 1. 상단: XPG LANCER RGB 메모리 독립 패널 (네모칸 1)
        # ==========================================
        self.ram_frame = QFrame(self)
        self.ram_frame.setObjectName("ram_frame")
        ram_layout = QVBoxLayout(self.ram_frame)
        ram_layout.setContentsMargins(16, 12, 16, 12)
        ram_layout.setSpacing(8)

        ram_title_h = QHBoxLayout()
        ram_title_h.setSpacing(8)
        ram_title_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        ram_photo_path = get_resource_path("assets/ram_photo.png")
        if os.path.exists(ram_photo_path):
            self.ram_img_lbl = QLabel()
            pix = QPixmap(ram_photo_path).scaled(80, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ram_img_lbl.setPixmap(pix)
            ram_title_h.addWidget(self.ram_img_lbl)

        hw_ram = HardwareDetector.get_ram_info()
        hw_ssd = HardwareDetector.get_ssd_info()
        hw_audio = HardwareDetector.get_audio_info()

        self.ram_title = QLabel(hw_ram["model"])
        self.ram_title.setFont(get_font_bold(15))
        ram_title_h.addWidget(self.ram_title)
        ram_title_h.addStretch()
        ram_layout.addLayout(ram_title_h)

        self.ram_badge = XpgLancerBadge(parent=self.ram_frame)
        ram_layout.addWidget(self.ram_badge)

        mem_h = QHBoxLayout()
        self.mem_tag = QLabel("Used Memory")
        self.mem_tag.setFont(get_font_bold(11))
        self.mem_val_lbl = QLabel("4,500 MB (7.2%)")
        self.mem_val_lbl.setFont(get_font_bold(12))
        mem_h.addWidget(self.mem_tag)
        mem_h.addStretch()
        mem_h.addWidget(self.mem_val_lbl)
        ram_layout.addLayout(mem_h)

        self.mem_bar = PCBProgressBar(max_val=100.0, height=12, parent=self.ram_frame)
        ram_layout.addWidget(self.mem_bar)

        # 타이밍 스펙
        timings_grid = QGridLayout()
        timings_grid.setContentsMargins(0, 4, 0, 2)
        timings_grid.setVerticalSpacing(3)
        timings_grid.setHorizontalSpacing(10)

        specs = [
            ("Timings", "30-36-36-76 CR1"),
            ("Speed", "DDR5-6000"),
            ("Voltage", "1.350 V"),
            ("FCLK", "2000 MHz"),
        ]

        for row, (k, v) in enumerate(specs):
            lbl_k = QLabel(k)
            lbl_k.setFont(get_font_regular(10))
            lbl_v = QLabel(v)
            lbl_v.setFont(get_font_bold(11))
            lbl_v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            timings_grid.addWidget(lbl_k, row, 0)
            timings_grid.addWidget(lbl_v, row, 1)
            self.spec_labels.append((lbl_k, lbl_v))

        ram_layout.addLayout(timings_grid)
        main_layout.addWidget(self.ram_frame, stretch=4)

        # ==========================================
        # 2. 중앙: 사선 챔퍼 시계 바
        # ==========================================
        self.clock_bar = ClockLogoBar(parent=self)
        main_layout.addWidget(self.clock_bar, stretch=0)

        # ==========================================
        # 3. 스토리지(SSD) & 쿨링 팬 독립 패널 (네모칸 2)
        # ※ SSD 아이콘 배지 삭제, 오직 실물 사진만 배치
        # ==========================================
        self.storage_frame = QFrame(self)
        self.storage_frame.setObjectName("storage_frame")
        stor_layout = QVBoxLayout(self.storage_frame)
        stor_layout.setContentsMargins(16, 12, 16, 12)
        stor_layout.setSpacing(6)

        # SSD 헤더 (실물 사진 + 타이틀)
        ssd_title_h = QHBoxLayout()
        ssd_title_h.setSpacing(8)
        ssd_title_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        ssd_photo_path = get_resource_path("assets/ssd_photo.png")
        if os.path.exists(ssd_photo_path):
            self.ssd_img_lbl = QLabel()
            pix_ssd = QPixmap(ssd_photo_path).scaled(75, 21, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.ssd_img_lbl.setPixmap(pix_ssd)
            ssd_title_h.addWidget(self.ssd_img_lbl)

        self.ssd_tag = QLabel(hw_ssd["model"])
        self.ssd_tag.setFont(get_font_bold(13))
        ssd_title_h.addWidget(self.ssd_tag)
        ssd_title_h.addStretch()

        self.ssd_val_lbl = QLabel("501 GB / 930 GB")
        self.ssd_val_lbl.setFont(get_font_bold(11))
        ssd_title_h.addWidget(self.ssd_val_lbl)
        stor_layout.addLayout(ssd_title_h)

        # SSD 프로그레스 바
        self.ssd_bar = PCBProgressBar(max_val=100.0, height=11, parent=self.storage_frame)
        stor_layout.addWidget(self.ssd_bar)

        # SSD I/O 실시간 오실로스코프 및 쿨링 팬 나란히 배치
        io_fan_h = QHBoxLayout()
        io_fan_h.setSpacing(10)

        # 좌측: 디스크 I/O 활동 파형
        self.ssd_scope = MiniScopeGraph(max_points=24, show_labels=False, parent=self.storage_frame)
        self.ssd_scope.setFixedHeight(42)
        io_fan_h.addWidget(self.ssd_scope, stretch=1)

        # 우측: 회전 쿨링 팬
        fan_box = QHBoxLayout()
        fan_box.setSpacing(6)
        self.fan_badge = FanSpinBadge(parent=self.storage_frame)
        fan_box.addWidget(self.fan_badge)

        fan_texts = QVBoxLayout()
        fan_texts.setSpacing(2)
        self.cpu_fan_lbl = QLabel("CPU: 1140 RPM")
        self.cpu_fan_lbl.setFont(get_font_bold(10))
        self.gpu_fan_lbl = QLabel("GPU: 0 RPM")
        self.gpu_fan_lbl.setFont(get_font_regular(10))
        fan_texts.addWidget(self.cpu_fan_lbl)
        fan_texts.addWidget(self.gpu_fan_lbl)
        fan_box.addLayout(fan_texts)
        io_fan_h.addLayout(fan_box)

        stor_layout.addLayout(io_fan_h)
        main_layout.addWidget(self.storage_frame, stretch=3)

        # ==========================================
        # 4. 하단: 사운드 / 오디오 전용 독립 패널 (네모칸 3)
        # ==========================================
        self.audio_frame = QFrame(self)
        self.audio_frame.setObjectName("audio_frame")
        audio_layout = QVBoxLayout(self.audio_frame)
        audio_layout.setContentsMargins(16, 10, 16, 10)
        audio_layout.setSpacing(6)

        # 4-1. 상단: 실물 사진 에셋 + 타이틀/디바이스 + 선명한 음량 수치
        audio_top_h = QHBoxLayout()
        audio_top_h.setSpacing(8)
        audio_top_h.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        audio_photo_path = get_resource_path("assets/audio_photo.png")
        self.audio_img_lbl = QLabel()
        if os.path.exists(audio_photo_path):
            pix_audio = QPixmap(audio_photo_path).scaled(46, 46, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.audio_img_lbl.setPixmap(pix_audio)
        audio_top_h.addWidget(self.audio_img_lbl)

        audio_texts = QVBoxLayout()
        audio_texts.setSpacing(2)
        self.audio_title_lbl = QLabel(hw_audio["title"])
        self.audio_title_lbl.setFont(get_font_bold(13))
        self.audio_dev_lbl = QLabel(hw_audio["device"])
        self.audio_dev_lbl.setFont(get_font_regular(10))
        audio_texts.addWidget(self.audio_title_lbl)
        audio_texts.addWidget(self.audio_dev_lbl)
        audio_top_h.addLayout(audio_texts)

        audio_top_h.addStretch()

        # 대형 음량(볼륨) 수치 표시 라벨
        self.audio_vol_lbl = QLabel("VOL 30%")
        self.audio_vol_lbl.setFont(get_font_bold(13))
        audio_top_h.addWidget(self.audio_vol_lbl)

        audio_layout.addLayout(audio_top_h)

        # 4-2. 하단: 실시간 볼륨 프로그레스 바 + 8밴드 점핑 VU 이퀄라이저
        audio_bot_h = QHBoxLayout()
        audio_bot_h.setSpacing(10)
        audio_bot_h.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.audio_bar = PCBProgressBar(max_val=100.0, height=11, parent=self.audio_frame)
        self.audio_bar.set_value(30.0)
        audio_bot_h.addWidget(self.audio_bar, stretch=1)

        self.vu_widget = AudioVuVisualizer(parent=self.audio_frame)
        audio_bot_h.addWidget(self.vu_widget, stretch=0)

        audio_layout.addLayout(audio_bot_h)
        main_layout.addWidget(self.audio_frame, stretch=2)

        self.apply_theme()

    def apply_theme(self):
        c_bg = WhitePCBColor.BG_PANEL.name()
        c_border = WhitePCBColor.BORDER_MAIN.name()
        c_main = WhitePCBColor.TEXT_MAIN.name()
        c_sub = WhitePCBColor.TEXT_SUB.name()
        c_muted = WhitePCBColor.TEXT_MUTED.name()

        frame_style = f"background-color: {c_bg}; border: 2.5px solid {c_border};"
        self.ram_frame.setStyleSheet(f"#ram_frame {{ {frame_style} }}")
        self.storage_frame.setStyleSheet(f"#storage_frame {{ {frame_style} }}")
        self.audio_frame.setStyleSheet(f"#audio_frame {{ {frame_style} }}")

        self.ram_title.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.mem_tag.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")
        self.mem_val_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")

        for lbl_k, lbl_v in self.spec_labels:
            lbl_k.setStyleSheet(f"color: {c_muted}; border: none; background: transparent;")
            lbl_v.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")

        self.ssd_tag.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.ssd_val_lbl.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")

        self.cpu_fan_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.gpu_fan_lbl.setStyleSheet(f"color: {c_sub}; border: none; background: transparent;")

        self.audio_title_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")
        self.audio_dev_lbl.setStyleSheet(f"color: {c_muted}; border: none; background: transparent;")
        self.audio_vol_lbl.setStyleSheet(f"color: {c_main}; border: none; background: transparent;")

        self.update()

    def update_data(self, mem_data, disk_data, cpu_fan, gpu_fan, audio_data=None):
        # 램 모델 및 사용량
        ram_model = mem_data.get('model')
        if ram_model and self.ram_title.text() != ram_model:
            self.ram_title.setText(ram_model)

        used_mb = int(mem_data['used_gb'] * 1024)
        pct = mem_data['percent']
        self.mem_val_lbl.setText(f"{used_mb:,} MB ({pct:.1f}%)")
        self.mem_bar.set_value(pct)

        # SSD 모델 및 사용량
        ssd_model = disk_data.get('model')
        if ssd_model and self.ssd_tag.text() != ssd_model:
            self.ssd_tag.setText(ssd_model)

        disk_used = int(disk_data['used_gb'])
        disk_total = int(disk_data['total_gb'])
        self.ssd_val_lbl.setText(f"{disk_used} GB / {disk_total} GB")
        self.ssd_bar.set_value(disk_data['percent'])
        io_activity = min(100.0, (disk_data['write_mb_s'] + disk_data['read_mb_s']) * 2.0)
        self.ssd_scope.add_point(io_activity)

        # 팬
        self.cpu_fan_lbl.setText(f"CPU: {cpu_fan} RPM")
        self.gpu_fan_lbl.setText(f"GPU: {gpu_fan}%")

        # 오디오
        if audio_data:
            title = audio_data.get("title")
            if title and self.audio_title_lbl.text() != title:
                self.audio_title_lbl.setText(title)
            dev = audio_data.get("device", "USB Audio Speakers")
            if dev and self.audio_dev_lbl.text() != dev:
                self.audio_dev_lbl.setText(dev)
            vol = audio_data.get("volume_percent", 30)
            muted = audio_data.get("muted", False)
            if muted:
                self.audio_vol_lbl.setText("MUTED")
                self.audio_vol_lbl.setStyleSheet("color: #ff3c50; border: none; background: transparent;")
                self.audio_bar.set_value(0.0)
            else:
                self.audio_vol_lbl.setText(f"VOL {vol}%")
                self.audio_vol_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()}; border: none; background: transparent;")
                self.audio_bar.set_value(vol)
            self.vu_widget.set_data(audio_data)
