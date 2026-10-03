"""
네온 발광 사이버펑크 듀얼 원형 아크 게이지 위젯
외부 링: 로드율(%), 내부 링: 온도(°C), 중심부 디지털 인디케이터
"""

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QConicalGradient, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import HUDColor, get_font_mono, get_font_display


class DualArcGauge(QWidget):
    """
    네온 사이버펑크 HUD 원형 듀얼 아크 계기판
    """
    def __init__(self, title="CPU LOAD", unit="%", max_val1=100.0, max_val2=100.0,
                 color1=HUDColor.CYAN, color2=HUDColor.MAGENTA, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.max_val1 = max_val1
        self.max_val2 = max_val2
        self.color1 = color1
        self.color2 = color2

        # 목표값 및 현재 부드러운 애니메이션 값
        self.target_val1 = 0.0
        self.curr_val1 = 0.0
        self.target_val2 = 0.0
        self.curr_val2 = 0.0

        self.sub_text1 = ""
        self.sub_text2 = ""

        self.setMinimumSize(220, 220)

        # 부드러운 보간 타이머 (60 FPS)
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(16)

    def set_values(self, val1, val2, sub1="", sub2=""):
        """val1: 로드율(%), val2: 온도(°C)"""
        self.target_val1 = float(max(0.0, min(self.max_val1, val1)))
        self.target_val2 = float(max(0.0, min(self.max_val2, val2)))
        self.sub_text1 = sub1
        self.sub_text2 = sub2

    def _update_animation(self):
        # 선형 보간 (Lerp)
        diff1 = self.target_val1 - self.curr_val1
        diff2 = self.target_val2 - self.curr_val2
        if abs(diff1) > 0.05 or abs(diff2) > 0.05:
            self.curr_val1 += diff1 * 0.15
            self.curr_val2 += diff2 * 0.15
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        center = QPointF(w / 2.0, h / 2.0)
        radius = min(w, h) / 2.0 - 16

        # 아크 범위: 시작 각도 150도에서 시계방향으로 240도
        # Qt 아크 각도 단위: 1/16도, 3시 방향이 0도, 반시계가 양수
        # 150도(8시 방향)에서 -240도(4시 방향)
        start_angle = 210 * 16
        span_total = -240 * 16

        # 1. 외곽 서브 틱(눈금) 드로잉
        painter.save()
        painter.translate(center)
        painter.setPen(QPen(HUDColor.BORDER_DIM, 1.0))
        ticks = 24
        for i in range(ticks + 1):
            deg = 150 + i * (240 / ticks)
            rad = math.radians(deg)
            r_out = radius + 6
            r_in = radius + (2 if i % 2 == 0 else 4)
            p1 = QPointF(r_in * math.cos(rad), r_in * math.sin(rad))
            p2 = QPointF(r_out * math.cos(rad), r_out * math.sin(rad))
            painter.drawLine(p1, p2)
        painter.restore()

        # 2. 외부 아크 (로드율) - 배경 트랙
        rect_out = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        track_pen = QPen(HUDColor.GRID_LINE, 8.0)
        track_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(track_pen)
        painter.drawArc(rect_out, start_angle, span_total)

        # 외부 아크 - 활성 네온 바
        ratio1 = self.curr_val1 / self.max_val1 if self.max_val1 > 0 else 0
        span1 = int(span_total * ratio1)

        # 글로우 효과
        glow_pen1 = QPen(QColor(self.color1.red(), self.color1.green(), self.color1.blue(), 50), 14.0)
        glow_pen1.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen1)
        painter.drawArc(rect_out, start_angle, span1)

        val_pen1 = QPen(self.color1, 8.0)
        val_pen1.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(val_pen1)
        painter.drawArc(rect_out, start_angle, span1)

        # 3. 내부 아크 (온도)
        r_inner = radius - 16
        rect_in = QRectF(center.x() - r_inner, center.y() - r_inner, r_inner * 2, r_inner * 2)
        track_pen_in = QPen(HUDColor.GRID_LINE, 6.0)
        track_pen_in.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(track_pen_in)
        painter.drawArc(rect_in, start_angle, span_total)

        ratio2 = self.curr_val2 / self.max_val2 if self.max_val2 > 0 else 0
        span2 = int(span_total * ratio2)

        # 온도에 따른 다이내믹 컬러 (65도 이상 앰버, 80도 이상 레드)
        dyn_color2 = self.color2
        if self.curr_val2 >= 80:
            dyn_color2 = HUDColor.RED
        elif self.curr_val2 >= 68:
            dyn_color2 = HUDColor.AMBER

        glow_pen2 = QPen(QColor(dyn_color2.red(), dyn_color2.green(), dyn_color2.blue(), 50), 11.0)
        glow_pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen2)
        painter.drawArc(rect_in, start_angle, span2)

        val_pen2 = QPen(dyn_color2, 6.0)
        val_pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(val_pen2)
        painter.drawArc(rect_in, start_angle, span2)

        # 4. 중앙 디지털 수치 표시
        # 상단 라벨
        painter.setFont(get_font_mono(9, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(center.x() - 70, center.y() - 48, 140, 18),
                         Qt.AlignmentFlag.AlignCenter, self.title)

        # 메인 대형 디지털 수치 (로드율 %)
        painter.setFont(get_font_display(26, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        main_val_str = f"{int(round(self.curr_val1))}{self.unit}"
        painter.drawText(QRectF(center.x() - 80, center.y() - 25, 160, 36),
                         Qt.AlignmentFlag.AlignCenter, main_val_str)

        # 보조 수치 (온도 °C)
        painter.setFont(get_font_mono(13, bold=True))
        painter.setPen(QPen(dyn_color2))
        temp_str = f"TEMP {int(round(self.curr_val2))}°C"
        painter.drawText(QRectF(center.x() - 70, center.y() + 14, 140, 22),
                         Qt.AlignmentFlag.AlignCenter, temp_str)

        # 최하단 서브 텍스트 (클럭 또는 RPM)
        if self.sub_text1:
            painter.setFont(get_font_mono(9))
            painter.setPen(QPen(HUDColor.TEXT_SECONDARY))
            painter.drawText(QRectF(center.x() - 80, center.y() + 38, 160, 18),
                             Qt.AlignmentFlag.AlignCenter, self.sub_text1)
