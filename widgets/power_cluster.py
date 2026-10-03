"""
슈퍼카 계기판 스타일 중앙 파워 & 메모리 텔레메트리 클러스터
GPU TGP 전력 소모(300W Cap), DDR5 64GB RAM, GDDR7 16GB VRAM, NVMe & 네트워크 통합
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF
from theme import HUDColor, get_font_mono, get_font_display


class PowerClusterWidget(QWidget):
    """
    중앙 텔레메트리 클러스터
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.power_w = 0.0
        self.power_limit_w = 300.0
        
        self.ram_used = 0.0
        self.ram_total = 64.0
        self.ram_pct = 0.0

        self.vram_used = 0.0
        self.vram_total = 16.0
        self.vram_pct = 0.0

        self.disk_read = 0.0
        self.disk_write = 0.0
        self.disk_temp = 0.0

        self.net_down = 0.0
        self.net_up = 0.0

        self.setMinimumSize(380, 270)

    def set_data(self, gpu_data, mem_data, disk_data, net_data):
        self.power_w = gpu_data.get('power_w', 0.0)
        self.power_limit_w = gpu_data.get('power_limit_w', 300.0)

        self.ram_used = mem_data.get('used_gb', 0.0)
        self.ram_total = mem_data.get('total_gb', 64.0)
        self.ram_pct = mem_data.get('percent', 0.0)

        self.vram_used = gpu_data.get('vram_used_mb', 0.0) / 1024.0
        self.vram_total = gpu_data.get('vram_total_mb', 16303.0) / 1024.0
        self.vram_pct = gpu_data.get('vram_percent', 0.0)

        self.disk_read = disk_data.get('read_mb_s', 0.0)
        self.disk_write = disk_data.get('write_mb_s', 0.0)
        self.disk_temp = disk_data.get('temp_c', 0.0)

        self.net_down = net_data.get('down_mb_s', 0.0)
        self.net_up = net_data.get('up_mb_s', 0.0)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # ==========================================
        # 1. GPU TGP 소비전력 (상단 대형 계기판)
        # ==========================================
        pwr_y = 6.0
        painter.setFont(get_font_mono(9, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_SECONDARY))
        painter.drawText(QRectF(10, pwr_y, 140, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "GPU REALTIME POWER")

        # 전력 수치 (20pt 볼드 앰버)
        pwr_ratio = min(1.0, max(0.0, self.power_w / self.power_limit_w if self.power_limit_w > 0 else 0))
        pwr_color = HUDColor.RED if pwr_ratio >= 0.85 else (HUDColor.GOLD if pwr_ratio >= 0.50 else HUDColor.CYAN)
        
        painter.setFont(get_font_display(18, bold=True))
        painter.setPen(QPen(pwr_color))
        painter.drawText(QRectF(w - 180, pwr_y - 2, 170, 24), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                         f"{self.power_w:.1f}W / {int(self.power_limit_w)}W")

        # 전력 메카닉 바 게이지
        bar_y1 = pwr_y + 24.0
        bar_w1 = w - 20.0
        bar_h1 = 14.0

        painter.setBrush(QBrush(HUDColor.BG_CARD_LIGHT))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 0.8))
        painter.drawRect(QRectF(10, bar_y1, bar_w1, bar_h1))

        fill_pw = bar_w1 * pwr_ratio
        if fill_pw > 0:
            grad1 = QLinearGradient(10, bar_y1, 10 + fill_pw, bar_y1)
            grad1.setColorAt(0.0, HUDColor.CYAN)
            grad1.setColorAt(0.6, HUDColor.GOLD)
            grad1.setColorAt(1.0, HUDColor.RED)
            painter.setBrush(QBrush(grad1))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(10, bar_y1, fill_pw, bar_h1))

        # ==========================================
        # 2. DDR5 시스템 메모리 & GDDR7 VRAM 듀얼 게이지
        # ==========================================
        def draw_mem_meter(y, label, used, total, pct, color):
            painter.setFont(get_font_mono(8, bold=True))
            painter.setPen(QPen(HUDColor.TEXT_TITLE))
            painter.drawText(QRectF(10, y, 175, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, label)

            painter.setPen(QPen(color))
            val_s = f"{used:.1f} / {total:.1f} GB ({pct:.1f}%)"
            painter.drawText(QRectF(w - 200, y, 190, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, val_s)

            my = y + 20.0
            mw = w - 20.0
            mh = 11.0
            segments = 28
            gap = 2.0
            seg_w = (mw - (segments - 1) * gap) / segments
            active_segs = int(round(segments * (pct / 100.0)))

            for i in range(segments):
                sx = 10 + i * (seg_w + gap)
                srect = QRectF(sx, my, seg_w, mh)
                if i < active_segs:
                    sc = HUDColor.RED if i / segments > 0.85 else (HUDColor.GOLD if i / segments > 0.70 else color)
                    painter.setBrush(QBrush(sc))
                else:
                    painter.setBrush(QBrush(HUDColor.GRID_LINE))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(srect)

        draw_mem_meter(bar_y1 + 24.0, "SYS RAM (DDR5 64GB)", self.ram_used, self.ram_total, self.ram_pct, HUDColor.CYAN)
        draw_mem_meter(bar_y1 + 62.0, "GPU VRAM (GDDR7 16GB)", self.vram_used, self.vram_total, self.vram_pct, HUDColor.MAGENTA)

        # ==========================================
        # 3. 하단 I/O & 네트워크 실시간 스피드 박스
        # ==========================================
        box_y = bar_y1 + 94.0
        box_w = (w - 28.0) / 2.0
        box_h = 56.0

        # 좌측: NVMe SSD 상태
        b1_rect = QRectF(10, box_y, box_w, box_h)
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 0.8))
        painter.drawRect(b1_rect)

        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_SECONDARY))
        painter.drawText(QRectF(16, box_y + 4, box_w - 12, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "NVMe SSD I/O")

        painter.setFont(get_font_mono(8))
        painter.setPen(QPen(HUDColor.GREEN))
        painter.drawText(QRectF(16, box_y + 20, box_w - 12, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"R: {self.disk_read:.1f} MB/s | W: {self.disk_write:.1f} MB/s")

        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(16, box_y + 36, box_w - 12, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"TEMP: {self.disk_temp:.1f}°C (SAMSUNG 980)")

        # 우측: 네트워크 대역폭
        b2_rect = QRectF(18 + box_w, box_y, box_w, box_h)
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.setPen(QPen(HUDColor.BORDER_DIM, 0.8))
        painter.drawRect(b2_rect)

        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_SECONDARY))
        painter.drawText(QRectF(24 + box_w, box_y + 4, box_w - 12, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "NETWORK TRAFFIC")

        painter.setFont(get_font_mono(8))
        painter.setPen(QPen(HUDColor.PURPLE))
        painter.drawText(QRectF(24 + box_w, box_y + 20, box_w - 12, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"DOWN: {self.net_down:.2f} MB/s")

        painter.setPen(QPen(HUDColor.GOLD))
        painter.drawText(QRectF(24 + box_w, box_y + 36, box_w - 12, 16), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"UP:   {self.net_up:.2f} MB/s (2.5GbE LAN)")
