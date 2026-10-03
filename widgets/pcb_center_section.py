"""
화이트 PCB AIDA64 센서 패널 - 중앙 섹션 (정밀 튜닝 버전)
Trident Z RGB 메모리 모듈, 사선 시계/로고 바, SSD 스토리지, 쿨링 팬, 네트워크 대역폭
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, get_font_bold, get_font_regular
from widgets.pcb_components import TridentZBadge
from widgets.pcb_bar import PCBProgressBar
from widgets.pcb_panels import ClockLogoBar
from widgets.mini_scope import MiniScopeGraph


class SsdIconBadge(QWidget):
    """레퍼런스 이미지의 SSD 드라이브 아이콘"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(52, 62)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        rect = QRectF(3, 3, w - 6, h - 6)

        painter.setBrush(QBrush(QColor(50, 54, 65)))
        painter.setPen(QPen(QColor(25, 28, 35), 2.0))
        painter.drawRoundedRect(rect, 4, 4)

        painter.setBrush(QBrush(QColor(200, 205, 215)))
        painter.setPen(Qt.PenStyle.NoPen)
        for pt in [QPointF(8, 8), QPointF(w - 8, 8), QPointF(8, h - 8), QPointF(w - 8, h - 8)]:
            painter.drawEllipse(pt, 2.0, 2.0)

        painter.setFont(get_font_bold(10))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "SSD")


class FanSpinBadge(QWidget):
    """레퍼런스 이미지의 회전하는 쿨링 팬 아이콘"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(44, 44)
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

        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 2.0))
        painter.setBrush(QBrush(QColor(45, 48, 58)))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.fan_angle)
        painter.setPen(QPen(Qt.GlobalColor.white, 2.0))
        for i in range(5):
            painter.rotate(72)
            painter.drawLine(0, 0, 0, int(r - 4))
        painter.restore()


class PcbCenterSection(QWidget):
    """
    화이트 PCB 센서패널 중앙 섹션 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(12)

        # ==========================================
        # 1. 상단: Trident Z RGB 메모리 모듈 패널
        # ==========================================
        self.ram_frame = QFrame(self)
        self.ram_frame.setObjectName("ram_frame")
        self.ram_frame.setStyleSheet(
            f"#ram_frame {{ background-color: {WhitePCBColor.BG_PANEL.name()}; border: 2.5px solid {WhitePCBColor.BORDER_MAIN.name()}; }}"
        )
        ram_layout = QVBoxLayout(self.ram_frame)
        ram_layout.setContentsMargins(16, 14, 16, 14)
        ram_layout.setSpacing(8)

        ram_title = QLabel("Trident Z RGB (DDR5 64GB)")
        ram_title.setFont(get_font_bold(16))
        ram_title.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()}; border: none; background: transparent;")
        ram_layout.addWidget(ram_title)

        # RGB 램 히트싱크 그래픽
        self.ram_badge = TridentZBadge(parent=self.ram_frame)
        ram_layout.addWidget(self.ram_badge)

        # Used Memory
        mem_h = QHBoxLayout()
        mem_tag = QLabel("Used Memory")
        mem_tag.setFont(get_font_bold(10))
        mem_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()}; border: none; background: transparent;")
        self.mem_val_lbl = QLabel("4,500 MB (7.2%)")
        self.mem_val_lbl.setFont(get_font_bold(10))
        self.mem_val_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()}; border: none; background: transparent;")
        mem_h.addWidget(mem_tag)
        mem_h.addStretch()
        mem_h.addWidget(self.mem_val_lbl)
        ram_layout.addLayout(mem_h)

        # 메모리 프로그레스 바
        self.mem_bar = PCBProgressBar(max_val=100.0, height=12, parent=self.ram_frame)
        ram_layout.addWidget(self.mem_bar)

        # 세부 타이밍 스펙 (레퍼런스 스타일 2열)
        timings_grid = QGridLayout()
        timings_grid.setContentsMargins(0, 4, 0, 0)
        timings_grid.setVerticalSpacing(2)

        def make_spec_lbl(text, is_val=False):
            lbl = QLabel(text)
            lbl.setFont(get_font_bold(8) if is_val else get_font_regular(8))
            lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name() if is_val else WhitePCBColor.TEXT_MUTED.name()}; border: none; background: transparent;")
            return lbl

        timings_grid.addWidget(make_spec_lbl("Timings"), 0, 0)
        timings_grid.addWidget(make_spec_lbl("30-36-36-76 CR1", True), 0, 1)
        timings_grid.addWidget(make_spec_lbl("Speed"), 1, 0)
        timings_grid.addWidget(make_spec_lbl("DDR5-6000", True), 1, 1)

        timings_grid.addWidget(make_spec_lbl("Voltage"), 0, 2)
        timings_grid.addWidget(make_spec_lbl("1.350 V", True), 0, 3)
        timings_grid.addWidget(make_spec_lbl("FCLK"), 1, 2)
        timings_grid.addWidget(make_spec_lbl("2000 MHz", True), 1, 3)

        ram_layout.addLayout(timings_grid)
        main_layout.addWidget(self.ram_frame, stretch=4)

        # ==========================================
        # 2. 중앙: 시계 & 게이밍 로고 바
        # ==========================================
        self.clock_bar = ClockLogoBar(parent=self)
        main_layout.addWidget(self.clock_bar, stretch=0)

        # ==========================================
        # 3. 하단: 스토리지 / 팬 / 네트워크 통합 패널
        # ==========================================
        self.bottom_frame = QFrame(self)
        self.bottom_frame.setObjectName("bottom_frame")
        self.bottom_frame.setStyleSheet(
            f"#bottom_frame {{ background-color: {WhitePCBColor.BG_PANEL.name()}; border: 2.5px solid {WhitePCBColor.BORDER_MAIN.name()}; }}"
        )
        bot_layout = QVBoxLayout(self.bottom_frame)
        bot_layout.setContentsMargins(16, 14, 16, 14)
        bot_layout.setSpacing(10)

        # [SSD 행]
        ssd_h = QHBoxLayout()
        ssd_h.setSpacing(10)
        self.ssd_badge = SsdIconBadge(parent=self.bottom_frame)
        ssd_h.addWidget(self.ssd_badge)

        ssd_info = QVBoxLayout()
        ssd_lbl_h = QHBoxLayout()
        ssd_tag = QLabel("C: Used (Samsung 980 Pro)")
        ssd_tag.setFont(get_font_bold(9))
        ssd_tag.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()}; border: none; background: transparent;")
        self.ssd_val_lbl = QLabel("501 GB / 930 GB")
        self.ssd_val_lbl.setFont(get_font_bold(9))
        self.ssd_val_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()}; border: none; background: transparent;")
        ssd_lbl_h.addWidget(ssd_tag)
        ssd_lbl_h.addStretch()
        ssd_lbl_h.addWidget(self.ssd_val_lbl)
        ssd_info.addLayout(ssd_lbl_h)

        self.ssd_bar = PCBProgressBar(max_val=100.0, height=10, parent=self.bottom_frame)
        ssd_info.addWidget(self.ssd_bar)

        # SSD 실시간 활동 미니 스코프
        self.ssd_scope = MiniScopeGraph(max_points=24, show_labels=False, parent=self.bottom_frame)
        self.ssd_scope.setFixedHeight(40)
        ssd_info.addWidget(self.ssd_scope)

        ssd_h.addLayout(ssd_info)
        bot_layout.addLayout(ssd_h)

        # 구분선
        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {WhitePCBColor.BORDER_LIGHT.name()}; border: none;")
        bot_layout.addWidget(sep)

        # [팬 & 네트워크 듀얼 행]
        dual_h = QHBoxLayout()
        dual_h.setSpacing(16)

        # 좌측: 쿨링 팬
        fan_box = QHBoxLayout()
        self.fan_badge = FanSpinBadge(parent=self.bottom_frame)
        fan_box.addWidget(self.fan_badge)

        fan_texts = QVBoxLayout()
        fan_texts.setSpacing(3)
        self.cpu_fan_lbl = QLabel("CPU: 1140 RPM")
        self.cpu_fan_lbl.setFont(get_font_bold(9))
        self.cpu_fan_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()}; border: none; background: transparent;")
        self.gpu_fan_lbl = QLabel("GPU: 0 RPM (IDLE)")
        self.gpu_fan_lbl.setFont(get_font_bold(9))
        self.gpu_fan_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()}; border: none; background: transparent;")
        fan_texts.addWidget(self.cpu_fan_lbl)
        fan_texts.addWidget(self.gpu_fan_lbl)
        fan_box.addLayout(fan_texts)
        dual_h.addLayout(fan_box)

        # 우측: 네트워크
        net_box = QVBoxLayout()
        net_box.setSpacing(3)
        self.net_down_lbl = QLabel("▼ 0.6 MB/s (DOWN)")
        self.net_down_lbl.setFont(get_font_bold(9))
        self.net_down_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_MAIN.name()}; border: none; background: transparent;")
        self.net_up_lbl = QLabel("▲ 0.0 MB/s (UP)")
        self.net_up_lbl.setFont(get_font_bold(9))
        self.net_up_lbl.setStyleSheet(f"color: {WhitePCBColor.TEXT_SUB.name()}; border: none; background: transparent;")
        net_box.addWidget(self.net_down_lbl)
        net_box.addWidget(self.net_up_lbl)
        dual_h.addLayout(net_box)

        bot_layout.addLayout(dual_h)
        main_layout.addWidget(self.bottom_frame, stretch=5)

    def update_data(self, mem_data, disk_data, net_data, cpu_fan, gpu_fan):
        # 램
        used_mb = int(mem_data['used_gb'] * 1024)
        pct = mem_data['percent']
        self.mem_val_lbl.setText(f"{used_mb:,} MB ({pct:.1f}%)")
        self.mem_bar.set_value(pct)

        # SSD
        disk_used = int(disk_data['used_gb'])
        disk_total = int(disk_data['total_gb'])
        self.ssd_val_lbl.setText(f"{disk_used} GB / {disk_total} GB")
        self.ssd_bar.set_value(disk_data['percent'])
        io_activity = min(100.0, (disk_data['write_mb_s'] + disk_data['read_mb_s']) * 2.0)
        self.ssd_scope.add_point(io_activity)

        # 팬
        self.cpu_fan_lbl.setText(f"CPU: {cpu_fan} RPM")
        self.gpu_fan_lbl.setText(f"GPU: {gpu_fan}%")

        # 네트워크
        self.net_down_lbl.setText(f"▼ {net_data['down_mb_s']:.1f} MB/s (DOWN)")
        self.net_up_lbl.setText(f"▲ {net_data['up_mb_s']:.1f} MB/s (UP)")
