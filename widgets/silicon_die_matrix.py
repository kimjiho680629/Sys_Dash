"""
AMD Ryzen 7 9800X3D 실리콘 다이(CCD) 8-Core / 16-Thread 매트릭스 위젯 (고밀도 튜닝 버전)
Zen 5 코어 칩셋 아키텍처, 3D V-Cache 태그, 실시간 부스트 클럭(5.2GHz), SMT 스레드 게이지
"""

from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF
from theme import HUDColor, get_font_mono


class CoreSiliconBlock(QWidget):
    """
    단일 물리 코어 (2개 논리 스레드 T0, T1 내장) 고밀도 실리콘 블록
    """
    def __init__(self, core_id=0, parent=None):
        super().__init__(parent)
        self.cid = core_id
        self.t0_id = core_id * 2
        self.t1_id = core_id * 2 + 1
        
        self.freq_mhz = 0
        self.t0_pct = 0.0
        self.t1_pct = 0.0
        self.avg_pct = 0.0

        self.setMinimumHeight(86)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_data(self, freq, t0_p, t1_p):
        self.freq_mhz = freq
        self.t0_pct = max(0.0, min(100.0, t0_p))
        self.t1_pct = max(0.0, min(100.0, t1_p))
        self.avg_pct = (self.t0_pct + self.t1_pct) / 2.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 코어 실리콘 칩 배경 (부하에 따른 네온 틴트)
        load_tint = int((self.avg_pct / 100.0) * 80)
        bg_r = min(255, 14 + load_tint)
        bg_g = min(255, 22 + int(load_tint * 0.4))
        bg_b = min(255, 42 + load_tint)
        painter.setBrush(QBrush(QColor(bg_r, bg_g, bg_b, 235)))

        is_boosted = (self.freq_mhz >= 5000)
        border_c = HUDColor.CYAN if is_boosted else HUDColor.BORDER_DIM
        painter.setPen(QPen(border_c, 1.5 if is_boosted else 0.8))
        painter.drawRect(QRectF(1, 1, w - 2, h - 2))

        # 2. 코어 헤더 (CORE 00 및 실시간 클럭)
        painter.setFont(get_font_mono(9, bold=True))
        painter.setPen(QPen(HUDColor.CYAN if is_boosted else HUDColor.TEXT_TITLE))
        painter.drawText(QRectF(8, 6, 65, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"CORE #{self.cid:02d}")

        # 클럭 수치 (5.0GHz 이상 골드, 4.5GHz 이상 시안)
        freq_color = HUDColor.GOLD if self.freq_mhz >= 5100 else (HUDColor.CYAN if self.freq_mhz >= 4500 else HUDColor.TEXT_MUTED)
        painter.setPen(QPen(freq_color))
        freq_str = f"{self.freq_mhz:,} MHz" if self.freq_mhz > 0 else "IDLE"
        painter.drawText(QRectF(w - 95, 6, 88, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, freq_str)

        # 3. 서브 태그: 3D V-Cache & Core Load Avg
        painter.setFont(get_font_mono(7))
        painter.setPen(QPen(HUDColor.PURPLE if self.cid < 4 else HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(8, 22, 110, 14), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "96MB V-CACHE")

        painter.setPen(QPen(HUDColor.TEXT_SECONDARY))
        painter.drawText(QRectF(w - 80, 22, 72, 14), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"AVG {int(round(self.avg_pct))}%")

        # 4. 개별 스레드 굵은 게이지 바 (T0 및 T1)
        def draw_thread_row(y_pos, tid, pct):
            # 라벨
            painter.setFont(get_font_mono(8, bold=True))
            painter.setPen(QPen(HUDColor.CYAN_DIM))
            painter.drawText(QRectF(8, y_pos, 24, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"T{tid:02d}")

            # 슬롯
            bx = 36.0
            bw = w - bx - 42.0
            bh = 9.0
            by = y_pos + 4.5

            painter.setBrush(QBrush(HUDColor.BG_CARD_LIGHT))
            painter.setPen(QPen(HUDColor.GRID_LINE, 0.5))
            painter.drawRect(QRectF(bx, by, bw, bh))

            # 채우기
            fill_w = bw * (pct / 100.0)
            if fill_w > 0:
                bar_c = HUDColor.RED if pct >= 80 else (HUDColor.GOLD if pct >= 50 else HUDColor.CYAN)
                grad = QLinearGradient(bx, by, bx + fill_w, by)
                grad.setColorAt(0.0, HUDColor.PURPLE)
                grad.setColorAt(1.0, bar_c)
                painter.setBrush(QBrush(grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(bx, by, fill_w, bh))

            # 수치 %
            painter.setFont(get_font_mono(8, bold=True))
            painter.setPen(QPen(HUDColor.TEXT_TITLE))
            painter.drawText(QRectF(w - 36, y_pos, 32, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{int(round(pct))}%")

        draw_thread_row(38.0, self.t0_id, self.t0_pct)
        draw_thread_row(58.0, self.t1_id, self.t1_pct)


class SiliconDieMatrix(QWidget):
    """
    8개 코어 블록(4열 2행)을 품은 AMD Zen 5 CCD 실리콘 다이 매트릭스
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.core_blocks = []

        grid = QGridLayout(self)
        grid.setContentsMargins(4, 4, 4, 4)
        grid.setSpacing(8)

        # 4열 2행 구조 (Core 0~3 상단, Core 4~7 하단)
        for i in range(8):
            row = i // 4
            col = i % 4
            block = CoreSiliconBlock(core_id=i, parent=self)
            self.core_blocks.append(block)
            grid.addWidget(block, row, col)

    def update_die(self, threads_pct, threads_freq):
        for i in range(8):
            t0 = i * 2
            t1 = i * 2 + 1
            p0 = threads_pct[t0] if t0 < len(threads_pct) else 0.0
            p1 = threads_pct[t1] if t1 < len(threads_pct) else 0.0
            f0 = threads_freq[t0] if t0 < len(threads_freq) else 0
            f1 = threads_freq[t1] if t1 < len(threads_freq) else 0
            avg_f = max(f0, f1)
            self.core_blocks[i].set_data(avg_f, p0, p1)
