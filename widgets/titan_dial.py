"""
AIDA64 / 슈퍼카 클러스터 스타일 타이탄 타코미터 다이얼 위젯 (정밀 튜닝 버전)
타코미터 눈금 숫자 마킹 (0, 20, 40, 60, 80, 100), 네온 니들(Needle), 대형 빅 넘버
"""

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush, QLinearGradient, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import HUDColor, get_font_mono, get_font_display


class TitanDial(QWidget):
    """
    슈퍼카 계기판 스타일 고정밀 타이탄 타코미터 다이얼
    """
    def __init__(self, title="CPU TELEMETRY", unit="%", max_val1=100.0, max_val2=100.0,
                 primary_color=HUDColor.CYAN, secondary_color=HUDColor.MAGENTA, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.max_val1 = max_val1
        self.max_val2 = max_val2
        self.primary_color = primary_color
        self.secondary_color = secondary_color

        self.target_val1 = 0.0
        self.curr_val1 = 0.0
        self.target_val2 = 0.0
        self.curr_val2 = 0.0

        self.sub_label = ""
        self.sub_val = ""

        # 회전 링 & 펄스
        self.rot_angle = 0.0
        self.pulse_val = 0.0
        self.pulse_dir = 1

        self.setMinimumSize(320, 310)

        # 60 FPS 보간 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(16)

    def set_values(self, val1, val2, sub_label="", sub_val=""):
        self.target_val1 = float(max(0.0, min(self.max_val1, val1)))
        self.target_val2 = float(max(0.0, min(self.max_val2, val2)))
        self.sub_label = sub_label
        self.sub_val = sub_val

    def _on_tick(self):
        diff1 = self.target_val1 - self.curr_val1
        diff2 = self.target_val2 - self.curr_val2
        if abs(diff1) > 0.04 or abs(diff2) > 0.04:
            self.curr_val1 += diff1 * 0.18
            self.curr_val2 += diff2 * 0.18

        self.rot_angle = (self.rot_angle + 0.4) % 360

        if self.curr_val2 >= 80:
            self.pulse_val += 0.06 * self.pulse_dir
            if self.pulse_val >= 1.0:
                self.pulse_val = 1.0
                self.pulse_dir = -1
            elif self.pulse_val <= 0.0:
                self.pulse_val = 0.0
                self.pulse_dir = 1
        else:
            self.pulse_val = 0.0

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        center = QPointF(w / 2.0, h / 2.0 + 4.0)
        radius = min(w, h) / 2.0 - 22.0

        start_angle = 210 * 16
        span_total = -240 * 16

        # 1. 과열 시 붉은 펄스 배경
        if self.pulse_val > 0.05:
            pulse_r = radius + 12
            glow_c = QColor(255, 42, 85, int(60 * self.pulse_val))
            painter.setBrush(QBrush(glow_c))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, pulse_r, pulse_r)

        # 2. 회전하는 은은한 사이버네틱 링
        painter.save()
        painter.translate(center)
        painter.rotate(self.rot_angle)
        dash_pen = QPen(HUDColor.GRID_LINE, 1.2, Qt.PenStyle.DotLine)
        painter.setPen(dash_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0, 0), radius - 36, radius - 36)
        painter.restore()

        # 3. 타코미터 정밀 눈금 및 숫자 마킹 (0, 20, 40, 60, 80, 100)
        painter.save()
        painter.translate(center)
        ticks = 50
        for i in range(ticks + 1):
            deg = 150 + i * (240 / ticks)
            rad = math.radians(deg)
            is_super = (i % 10 == 0)
            is_major = (i % 5 == 0)

            r_out = radius + (10 if is_super else (6 if is_major else 3))
            r_in = radius - (4 if is_super else 0)

            t_color = HUDColor.BORDER_HUD if is_super else (HUDColor.BORDER_DIM if is_major else HUDColor.GRID_LINE)
            if deg >= 330 and is_major:
                t_color = HUDColor.RED
            elif deg >= 270 and is_major:
                t_color = HUDColor.GOLD

            painter.setPen(QPen(t_color, 2.0 if is_super else (1.2 if is_major else 0.8)))
            p1 = QPointF(r_in * math.cos(rad), r_in * math.sin(rad))
            p2 = QPointF(r_out * math.cos(rad), r_out * math.sin(rad))
            painter.drawLine(p1, p2)

            # 슈퍼 마커 숫자 라벨 (0, 20, 40, 60, 80, 100)
            if is_super:
                num_val = int((i / ticks) * 100)
                r_num = radius - 18
                nx = r_num * math.cos(rad)
                ny = r_num * math.sin(rad)
                painter.setFont(get_font_mono(7, bold=True))
                painter.setPen(QPen(HUDColor.TEXT_MUTED))
                painter.drawText(QRectF(nx - 14, ny - 8, 28, 16), Qt.AlignmentFlag.AlignCenter, str(num_val))
        painter.restore()

        # 4. 외부 아우터 림 (부하율 % 게이지)
        rect_out = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        base_track_pen = QPen(HUDColor.BG_CARD_LIGHT, 12.0)
        base_track_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(base_track_pen)
        painter.drawArc(rect_out, start_angle, span_total)

        ratio1 = min(1.0, max(0.0, self.curr_val1 / self.max_val1 if self.max_val1 > 0 else 0))
        span1 = int(span_total * ratio1)

        active_color = self.primary_color
        if self.curr_val1 >= 85:
            active_color = HUDColor.RED
        elif self.curr_val1 >= 60:
            active_color = HUDColor.GOLD

        # 글로우 & 메인 바
        glow_pen1 = QPen(QColor(active_color.red(), active_color.green(), active_color.blue(), 60), 22.0)
        glow_pen1.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen1)
        painter.drawArc(rect_out, start_angle, span1)

        val_pen1 = QPen(active_color, 12.0)
        val_pen1.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(val_pen1)
        painter.drawArc(rect_out, start_angle, span1)

        # 5. 내부 아크 (온도 °C 게이지)
        r_inner = radius - 26.0
        rect_in = QRectF(center.x() - r_inner, center.y() - r_inner, r_inner * 2, r_inner * 2)

        track_pen_in = QPen(HUDColor.GRID_LINE, 7.0)
        track_pen_in.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(track_pen_in)
        painter.drawArc(rect_in, start_angle, span_total)

        ratio2 = min(1.0, max(0.0, self.curr_val2 / self.max_val2 if self.max_val2 > 0 else 0))
        span2 = int(span_total * ratio2)

        temp_color = self.secondary_color
        if self.curr_val2 >= 80:
            temp_color = HUDColor.RED
        elif self.curr_val2 >= 68:
            temp_color = HUDColor.GOLD

        val_pen2 = QPen(temp_color, 7.0)
        val_pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(val_pen2)
        painter.drawArc(rect_in, start_angle, span2)

        # 6. 날렵한 슈퍼카 네온 바늘 (Tachometer Needle)
        painter.save()
        painter.translate(center)
        needle_deg = 150 + (ratio1 * 240.0)
        painter.rotate(needle_deg)

        needle_len = radius - 6.0
        needle_poly = QPolygonF([
            QPointF(0, -2.5),
            QPointF(needle_len, 0),
            QPointF(0, 2.5),
            QPointF(-10, 0)
        ])
        painter.setBrush(QBrush(active_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(needle_poly)

        # 바늘 끝 네온 점
        painter.setBrush(QBrush(HUDColor.TEXT_TITLE))
        painter.drawEllipse(QPointF(needle_len, 0), 2.5, 2.5)

        # 중앙 중심점 캡
        painter.setBrush(QBrush(HUDColor.BG_VOID))
        painter.setPen(QPen(active_color, 2.0))
        painter.drawEllipse(QPointF(0, 0), 8.0, 8.0)
        painter.restore()

        # 7. 중앙 초대형 빅 넘버 디스플레이
        painter.setFont(get_font_mono(10, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(center.x() - 110, center.y() - 72, 220, 20),
                         Qt.AlignmentFlag.AlignCenter, self.title)

        # 44pt 초대형 숫자
        painter.setFont(get_font_display(44, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_TITLE))
        main_val_str = f"{int(round(self.curr_val1))}{self.unit}"
        painter.drawText(QRectF(center.x() - 110, center.y() - 48, 220, 52),
                         Qt.AlignmentFlag.AlignCenter, main_val_str)

        # 온도 인디케이터
        painter.setFont(get_font_mono(15, bold=True))
        painter.setPen(QPen(temp_color))
        temp_str = f"TEMP {int(round(self.curr_val2))}°C"
        painter.drawText(QRectF(center.x() - 90, center.y() + 18, 180, 26),
                         Qt.AlignmentFlag.AlignCenter, temp_str)

        # 보조 텔레메트리 (RPM / 클럭)
        if self.sub_val:
            painter.setFont(get_font_mono(10, bold=True))
            painter.setPen(QPen(HUDColor.CYAN_DIM))
            sub_full = f"{self.sub_label}: {self.sub_val}" if self.sub_label else self.sub_val
            painter.drawText(QRectF(center.x() - 100, center.y() + 46, 200, 20),
                             Qt.AlignmentFlag.AlignCenter, sub_full)
