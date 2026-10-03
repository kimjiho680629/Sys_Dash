"""
화이트 PCB AIDA64 센서 패널 전용 하드웨어 아이콘 컴포넌트
CPU 소켓 칩, GPU 그래픽카드, 수온 물방울, VRM 칩, Trident Z RGB RAM, SSD, 쿨러 팬
"""

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QPainterPath, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, get_font_bold, get_font_regular


class CpuSocketBadge(QWidget):
    """
    레퍼런스 이미지 우측 상단의 CPU 소켓 패키지 온도 아이콘
    상하좌우 핀(Pins), 내부 블루-퍼플 그라디언트 코어, 대형 흰색 온도 숫자
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_c = 44
        self.setFixedSize(96, 96)

    def set_temp(self, temp):
        self.temp_c = int(round(temp))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cx = w / 2.0
        cy = h / 2.0

        # 1. 외곽 핀 (Pins: 금색/은색 소켓 단자)
        pin_c = QColor(160, 165, 175)
        painter.setPen(QPen(pin_c, 1.5))
        # 상하 핀
        for i in range(-3, 4):
            px = cx + i * 8.0
            painter.drawLine(QPointF(px, cy - 38), QPointF(px, cy - 32))
            painter.drawLine(QPointF(px, cy + 32), QPointF(px, cy + 38))
        # 좌우 핀
        for i in range(-3, 4):
            py = cy + i * 8.0
            painter.drawLine(QPointF(cx - 38, py), QPointF(cx - 32, py))
            painter.drawLine(QPointF(cx + 32, py), QPointF(cx + 38, py))

        # 2. 메인 CPU 기판 (어두운 챠콜 그레이 사각형)
        pkg_rect = QRectF(cx - 32, cy - 32, 64, 64)
        painter.setBrush(QBrush(QColor(42, 45, 54)))
        painter.setPen(QPen(QColor(25, 28, 35), 2.0))
        painter.drawRoundedRect(pkg_rect, 4, 4)

        # 3. 내부 IHS / 코어 다이 (블루-퍼플 그라디언트)
        core_rect = QRectF(cx - 24, cy - 24, 48, 48)
        grad = QLinearGradient(cx, cy - 24, cx, cy + 24)
        grad.setColorAt(0.0, WhitePCBColor.CHIP_BLUE_TOP)
        grad.setColorAt(0.55, WhitePCBColor.CHIP_BLUE_TOP)
        grad.setColorAt(0.85, WhitePCBColor.CHIP_PURPLE_BOT)
        grad.setColorAt(1.0, WhitePCBColor.CHIP_PURPLE_BOT)

        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(255, 255, 255, 220), 1.8))
        painter.drawRoundedRect(core_rect, 3, 3)

        # 4. 중앙 대형 흰색 온도 숫자
        painter.setFont(get_font_bold(22))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(core_rect, Qt.AlignmentFlag.AlignCenter, str(self.temp_c))


class GpuCardBadge(QWidget):
    """
    레퍼런스 이미지의 그래픽카드 외형 온도 아이콘
    좌측 대형 온도 숫자, 중앙 X자 네온 RGB 액센트, 우측 회전 쿨링 팬
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_c = 43
        self.fan_angle = 0.0
        self.setFixedSize(140, 52)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate_fan)
        self.timer.start(30)

    def _rotate_fan(self):
        self.fan_angle = (self.fan_angle + 6.0) % 360
        self.update()

    def set_temp(self, temp):
        self.temp_c = int(round(temp))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 그래픽카드 백플레이트 / 슈라우드 바디
        body_rect = QRectF(4, 4, w - 8, h - 8)
        painter.setBrush(QBrush(QColor(45, 48, 58)))
        painter.setPen(QPen(QColor(28, 30, 38), 2.0))
        painter.drawRoundedRect(body_rect, 4, 4)

        # 2. 좌측 온도 표시 구역
        temp_rect = QRectF(10, 4, 42, h - 8)
        painter.setFont(get_font_bold(20))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(temp_rect, Qt.AlignmentFlag.AlignCenter, str(self.temp_c))

        # 3. 중앙 X자 네온 RGB 액센트
        mid_x = 72.0
        cy = h / 2.0
        painter.setPen(QPen(WhitePCBColor.GPU_ACCENT, 2.5))
        painter.drawLine(QPointF(mid_x - 14, cy - 14), QPointF(mid_x + 14, cy + 14))
        painter.drawLine(QPointF(mid_x - 14, cy + 14), QPointF(mid_x + 14, cy - 14))

        # 4. 우측 회전 쿨링 팬
        fx = w - 26.0
        fy = cy
        fr = 14.0

        painter.setPen(QPen(QColor(180, 185, 195), 1.2))
        painter.setBrush(QBrush(QColor(25, 28, 35)))
        painter.drawEllipse(QPointF(fx, fy), fr, fr)

        painter.save()
        painter.translate(fx, fy)
        painter.rotate(self.fan_angle)
        blade_pen = QPen(Qt.GlobalColor.white, 2.0)
        painter.setPen(blade_pen)
        for i in range(5):
            painter.rotate(72)
            painter.drawLine(0, 0, 0, int(fr - 3))
        painter.restore()


class LiquidDropBadge(QWidget):
    """
    레퍼런스 이미지의 수온(Liquid Temp) 물방울 아이콘
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_c = 34
        self.setFixedSize(68, 70)

    def set_temp(self, temp):
        self.temp_c = int(round(temp))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cx = w / 2.0

        # 물방울 패스 드로잉
        path = QPainterPath()
        path.moveTo(cx, 6)
        path.cubicTo(cx + 28, 34, cx + 28, h - 8, cx, h - 8)
        path.cubicTo(cx - 28, h - 8, cx - 28, 34, cx, 6)

        painter.setBrush(QBrush(WhitePCBColor.WATER_DROP))
        painter.setPen(QPen(QColor(20, 22, 28), 2.0))
        painter.drawPath(path)

        # 온도 텍스트
        painter.setFont(get_font_bold(11))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(QRectF(0, 28, w, 32), Qt.AlignmentFlag.AlignCenter, f"{self.temp_c}°C")


class VrmChipBadge(QWidget):
    """
    레퍼런스 이미지의 전원부(VRM Temp) 모스펫 칩셋 아이콘
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_c = 50
        self.setFixedSize(68, 70)

    def set_temp(self, temp):
        self.temp_c = int(round(temp))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cx = w / 2.0

        # 상단 탭 (나사 구멍 있는 메탈 플레이트)
        tab_poly = QPolygonF([
            QPointF(cx - 18, 6),
            QPointF(cx + 18, 6),
            QPointF(cx + 24, 18),
            QPointF(cx - 24, 18)
        ])
        painter.setBrush(QBrush(QColor(180, 185, 195)))
        painter.setPen(QPen(QColor(140, 145, 155), 1.0))
        painter.drawPolygon(tab_poly)

        # 나사 구멍
        painter.setBrush(QBrush(QColor(60, 64, 75)))
        painter.drawEllipse(QPointF(cx, 12), 4.0, 4.0)

        # 칩 바디
        body_rect = QRectF(cx - 24, 18, 48, 36)
        painter.setBrush(QBrush(WhitePCBColor.VRM_CHIP))
        painter.setPen(QPen(QColor(25, 28, 35), 1.5))
        painter.drawRoundedRect(body_rect, 2, 2)

        # 하단 3개 핀
        painter.setPen(QPen(QColor(160, 165, 175), 2.5))
        for px in [cx - 14, cx, cx + 14]:
            painter.drawLine(QPointF(px, 54), QPointF(px, 64))

        # 온도 텍스트
        painter.setFont(get_font_bold(11))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(body_rect, Qt.AlignmentFlag.AlignCenter, f"{self.temp_c}°C")


class TridentZBadge(QWidget):
    """
    레퍼런스 이미지 우측의 Trident Z RGB 알루미늄 방열판 + 화려한 RGB 라이트 바 모듈
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(42)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        # 1. 상단 화려한 RGB 아크릴 라이트 바 (레퍼런스 이미지처럼 좌측은 블루/바이올렛, 우측은 컷아웃 슬릿)
        rgb_rect = QRectF(2, 4, w - 4, 10)
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, QColor(0, 140, 255))
        grad.setColorAt(0.4, QColor(60, 40, 240))
        grad.setColorAt(0.7, QColor(140, 0, 255))
        grad.setColorAt(1.0, QColor(220, 0, 180))

        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rgb_rect, 2, 2)

        # 2. 하단 브러시드 알루미늄 블랙/건메탈 방열판
        sink_poly = QPolygonF([
            QPointF(2, 13),
            QPointF(w - 2, 13),
            QPointF(w - 2, h - 4),
            QPointF(2, h - 4)
        ])
        painter.setBrush(QBrush(QColor(38, 41, 50)))
        painter.setPen(QPen(QColor(20, 22, 28), 1.5))
        painter.drawPolygon(sink_poly)

        # 방열판 우측의 상징적인 날렵한 사선 핀 슬릿 (Trident Z 고유 시그니처)
        painter.setPen(QPen(QColor(130, 0, 255), 2.2))
        for sx in [w - 35, w - 25, w - 15]:
            painter.drawLine(QPointF(sx - 4, 7), QPointF(sx + 2, 15))
