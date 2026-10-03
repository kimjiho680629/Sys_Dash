"""
AMD Ryzen 7 9800X3D 전용 16-스레드 실시간 매트릭스 위젯
각 스레드의 실시간 사용률(%), 주파수(MHz), 세그먼트 바 시각화
"""

from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF
from theme import HUDColor, get_font_mono


class ThreadBar(QWidget):
    """단일 스레드용 미니 사이버펑크 세그먼트 바"""
    def __init__(self, thread_id=0, parent=None):
        super().__init__(parent)
        self.tid = thread_id
        self.percent = 0.0
        self.freq_mhz = 0
        self.setFixedHeight(22)

    def set_data(self, percent, freq_mhz):
        self.percent = max(0.0, min(100.0, percent))
        self.freq_mhz = freq_mhz
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 배경 틴트
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 0.5))
        painter.drawRect(QRectF(0, 0, w, h))

        # 1. 스레드 라벨
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.CYAN_DIM))
        tid_str = f"T{self.tid:02d}"
        painter.drawText(QRectF(4, 0, 24, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, tid_str)

        # 2. 클럭 수치 (MHz)
        painter.setFont(get_font_mono(8))
        if self.freq_mhz >= 5000:
            painter.setPen(QPen(HUDColor.CYAN))
        elif self.freq_mhz >= 4000:
            painter.setPen(QPen(HUDColor.TEXT_BODY))
        else:
            painter.setPen(QPen(HUDColor.TEXT_MUTED))
        freq_str = f"{self.freq_mhz}M" if self.freq_mhz > 0 else "--"
        painter.drawText(QRectF(30, 0, 48, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, freq_str)

        # 3. 세그먼트 레벨 게이지 바 (중앙 영역)
        bar_x = 80
        bar_w = w - bar_x - 38
        bar_h = 8
        bar_y = (h - bar_h) / 2.0

        # 게이지 배경 슬롯
        painter.setBrush(QBrush(HUDColor.GRID_LINE))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(bar_x, bar_y, bar_w, bar_h))

        # 채워질 길이
        fill_w = bar_w * (self.percent / 100.0)
        if fill_w > 0:
            # 부하율에 따른 색상
            if self.percent >= 80:
                bar_color = HUDColor.RED
            elif self.percent >= 50:
                bar_color = HUDColor.AMBER
            else:
                bar_color = HUDColor.CYAN

            # 그라디언트 채우기
            grad = QLinearGradient(bar_x, bar_y, bar_x + fill_w, bar_y)
            grad.setColorAt(0.0, HUDColor.PURPLE)
            grad.setColorAt(1.0, bar_color)
            painter.setBrush(QBrush(grad))
            painter.drawRect(QRectF(bar_x, bar_y, fill_w, bar_h))

        # 4. 백분율 수치
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        pct_str = f"{int(round(self.percent)):3d}%"
        painter.drawText(QRectF(w - 36, 0, 32, h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, pct_str)


class Ryzen16ThreadMatrix(QWidget):
    """
    16스레드 2열 8행 레이아웃 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_bars = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # 좌측 열 (T00 ~ T07)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(4)
        for i in range(8):
            bar = ThreadBar(thread_id=i, parent=self)
            self.thread_bars.append(bar)
            left_layout.addWidget(bar)
        layout.addLayout(left_layout)

        # 우측 열 (T08 ~ T15)
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        for i in range(8, 16):
            bar = ThreadBar(thread_id=i, parent=self)
            self.thread_bars.append(bar)
            right_layout.addWidget(bar)
        layout.addLayout(right_layout)

    def update_threads(self, per_cpu_percent, per_cpu_freq):
        for i in range(min(16, len(self.thread_bars))):
            pct = per_cpu_percent[i] if i < len(per_cpu_percent) else 0.0
            freq = per_cpu_freq[i] if i < len(per_cpu_freq) else 0
            self.thread_bars[i].set_data(pct, freq)
