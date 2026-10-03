"""
사이버펑크 VRAM & 시스템 메모리 세그먼트 바 위젯
RAM(64GB) 및 RTX 5070 Ti VRAM(16GB) 실시간 점유율 시각화
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF
from theme import HUDColor, get_font_mono


class SegmentedMemoryBar(QWidget):
    """단일 메모리 트랙 (RAM 또는 VRAM)"""
    def __init__(self, label="RAM", color=HUDColor.CYAN, parent=None):
        super().__init__(parent)
        self.label = label
        self.color = color
        self.used_gb = 0.0
        self.total_gb = 16.0
        self.percent = 0.0
        self.setFixedHeight(34)

    def set_data(self, used_gb, total_gb, percent):
        self.used_gb = used_gb
        self.total_gb = total_gb
        self.percent = max(0.0, min(100.0, percent))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 텍스트 라벨 (상단)
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        painter.drawText(QRectF(0, 0, 80, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.label)

        # 수치 (우측 상단)
        val_str = f"{self.used_gb:.1f} / {self.total_gb:.1f} GB ({self.percent:.1f}%)"
        painter.setPen(QPen(self.color))
        painter.drawText(QRectF(80, 0, w - 80, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, val_str)

        # 2. 세그먼트 블록 게이지 (하단)
        bar_y = 18.0
        bar_h = 10.0
        segments = 30
        seg_gap = 2.0
        total_gaps = (segments - 1) * seg_gap
        seg_w = (w - total_gaps) / segments

        active_segs = int(round(segments * (self.percent / 100.0)))

        for i in range(segments):
            x = i * (seg_w + seg_gap)
            rect = QRectF(x, bar_y, seg_w, bar_h)

            if i < active_segs:
                # 활성 세그먼트 (점유율에 따라 색상 변화)
                seg_ratio = i / float(segments)
                if seg_ratio > 0.85:
                    c = HUDColor.RED
                elif seg_ratio > 0.70:
                    c = HUDColor.AMBER
                else:
                    c = self.color
                painter.setBrush(QBrush(c))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(rect)
            else:
                # 비활성 세그먼트
                painter.setBrush(QBrush(HUDColor.GRID_LINE))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(rect)


class DualMemoryWidget(QWidget):
    """RAM과 VRAM을 수직으로 결합한 통합 메모리 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.ram_bar = SegmentedMemoryBar(label="SYS RAM (DDR5)", color=HUDColor.CYAN, parent=self)
        self.vram_bar = SegmentedMemoryBar(label="GPU VRAM (GDDR7)", color=HUDColor.MAGENTA, parent=self)

        layout.addWidget(self.ram_bar)
        layout.addWidget(self.vram_bar)

    def update_memory(self, mem_data, gpu_data):
        self.ram_bar.set_data(mem_data['used_gb'], mem_data['total_gb'], mem_data['percent'])
        v_used = gpu_data['vram_used_mb'] / 1024.0
        v_total = gpu_data['vram_total_mb'] / 1024.0
        self.vram_bar.set_data(v_used, v_total, gpu_data['vram_percent'])
