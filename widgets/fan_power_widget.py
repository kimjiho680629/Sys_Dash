"""
GPU 소비전력, 클럭 주파수, 팬 속도(RPM) 모니터링 위젯
"""

import math
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import HUDColor, get_font_mono, get_font_display


class FanPowerWidget(QWidget):
    """
    GPU 파워 & 팬 속도 테크니컬 HUD 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.power_w = 0.0
        self.power_limit_w = 300.0
        self.clock_core = 0
        self.clock_mem = 0
        self.cpu_fan_rpm = 0
        self.gpu_fan_pct = 0

        # 팬 회전 애니메이션 각도
        self.fan_angle = 0.0
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._rotate_fan)
        self.anim_timer.start(25)

        self.setFixedHeight(80)

    def _rotate_fan(self):
        speed = 2.0 + (self.cpu_fan_rpm / 300.0)
        self.fan_angle = (self.fan_angle + speed) % 360
        self.update()

    def set_data(self, gpu_data, cpu_fan_rpm):
        self.power_w = gpu_data.get('power_w', 0.0)
        self.power_limit_w = gpu_data.get('power_limit_w', 300.0)
        self.clock_core = gpu_data.get('clock_core_mhz', 0)
        self.clock_mem = gpu_data.get('clock_mem_mhz', 0)
        self.gpu_fan_pct = gpu_data.get('fan_percent', 0)
        self.cpu_fan_rpm = cpu_fan_rpm

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 좌측 영역: 회전하는 쿨링팬 HUD 그래픽 & RPM
        cx, cy = 30.0, h / 2.0
        r = 22.0

        # 외곽 서클
        painter.setPen(QPen(HUDColor.CYAN_DIM, 1.5))
        painter.setBrush(QBrush(HUDColor.BG_CARD))
        painter.drawEllipse(QPointF(cx, cy), r, r)

        # 회전하는 3개 블레이드
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.fan_angle)
        blade_pen = QPen(HUDColor.CYAN, 2.5)
        painter.setPen(blade_pen)
        for i in range(3):
            painter.rotate(120)
            painter.drawLine(0, 0, 0, int(r - 5))
        painter.restore()

        # 팬 RPM 텍스트
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        painter.drawText(QRectF(60, 10, 120, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "CPU COOLER")

        painter.setFont(get_font_display(13, bold=True))
        painter.setPen(QPen(HUDColor.CYAN))
        painter.drawText(QRectF(60, 28, 120, 24), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"{self.cpu_fan_rpm} RPM")

        painter.setFont(get_font_mono(8))
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(60, 52, 120, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f"GPU FAN: {self.gpu_fan_pct}%")

        # 2. 중앙 영역: GPU 소비전력 (TGP Wattage)
        mid_x = w * 0.38
        mid_w = w * 0.32

        # 타이틀 & 실시간 소비 W
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        painter.drawText(QRectF(mid_x, 10, 100, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "GPU POWER")

        painter.setFont(get_font_mono(9, bold=True))
        painter.setPen(QPen(HUDColor.AMBER))
        pwr_str = f"{self.power_w:.1f}W"
        painter.drawText(QRectF(mid_x + 90, 10, mid_w - 90, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, pwr_str)

        # 파워 바 게이지
        p_ratio = min(1.0, max(0.0, self.power_w / self.power_limit_w if self.power_limit_w > 0 else 0))
        p_bar_y = 32.0
        p_bar_h = 10.0
        painter.setBrush(QBrush(HUDColor.GRID_LINE))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(mid_x, p_bar_y, mid_w, p_bar_h))

        fill_pw = mid_w * p_ratio
        if fill_pw > 0:
            grad = QLinearGradient(mid_x, p_bar_y, mid_x + fill_pw, p_bar_y)
            grad.setColorAt(0.0, HUDColor.CYAN)
            grad.setColorAt(0.7, HUDColor.AMBER)
            grad.setColorAt(1.0, HUDColor.RED)
            painter.setBrush(QBrush(grad))
            painter.drawRect(QRectF(mid_x, p_bar_y, fill_pw, p_bar_h))

        # 하단 리미트 수치
        painter.setFont(get_font_mono(8))
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(mid_x, 48, mid_w, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"TGP CAP: {int(self.power_limit_w)}W")

        # 3. 우측 영역: GPU 코어 & 메모리 클럭
        right_x = w * 0.74
        right_w = w - right_x - 10

        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        painter.drawText(QRectF(right_x, 10, right_w, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "GPU FREQUENCIES")

        painter.setFont(get_font_mono(9))
        painter.setPen(QPen(HUDColor.TEXT_BODY))
        painter.drawText(QRectF(right_x, 32, right_w, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"CORE:  {self.clock_core:,} MHz")
        painter.drawText(QRectF(right_x, 52, right_w, 18), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         f"VRAM: {self.clock_mem:,} MHz")
