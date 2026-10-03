"""
사이버네틱 메카닉 HUD 패널 컨테이너
헥사곤 메쉬 텍스처, 코너 육각 볼트 마킹, 챔퍼 테두리, 위기 경고 발광
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QRectF
from theme import HUDColor, get_font_mono, draw_hex_bolt, draw_hexagon_mesh


class HUDCard(QFrame):
    """
    고성능 메카닉 센서 패널 컨테이너
    """
    def __init__(self, title="// MODULE", tag="NOMINAL", parent=None):
        super().__init__(parent)
        self.title_text = title
        self.tag_text = tag
        self.accent_color = HUDColor.CYAN
        self.is_critical = False
        self.show_mesh = True

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(14, 30, 14, 14)
        self.main_layout.setSpacing(8)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def set_content_widget(self, widget: QWidget):
        self.main_layout.addWidget(widget)

    def set_accent_color(self, color: QColor):
        self.accent_color = color
        self.update()

    def set_critical(self, critical: bool):
        if self.is_critical != critical:
            self.is_critical = critical
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cut = 14.0  # 챔퍼 크기

        # 1. 배경 프레임 다각형
        bg_poly = QPolygonF([
            QPointF(cut, 0),
            QPointF(w - cut, 0),
            QPointF(w, cut),
            QPointF(w, h - cut),
            QPointF(w - cut, h),
            QPointF(cut, h),
            QPointF(0, h - cut),
            QPointF(0, cut)
        ])

        painter.setBrush(QBrush(HUDColor.BG_PANEL))
        current_border = HUDColor.RED if self.is_critical else HUDColor.BORDER_DIM
        painter.setPen(QPen(current_border, 1.2))
        painter.drawPolygon(bg_poly)

        # 2. 은은한 헥사곤 메쉬 배경 텍스처
        if self.show_mesh:
            draw_hexagon_mesh(painter, QRectF(2, 26, w - 4, h - 28), side=18.0)

        # 3. 상단 헤더 바
        header_poly = QPolygonF([
            QPointF(cut, 1),
            QPointF(w - cut, 1),
            QPointF(w - 1, cut),
            QPointF(w - 1, 24),
            QPointF(1, 24),
            QPointF(1, cut)
        ])
        painter.setBrush(QBrush(HUDColor.BG_CARD_LIGHT))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPolygon(header_poly)

        # 4. 코너 육각 볼트 마킹 (4개 모서리)
        draw_hex_bolt(painter, QPointF(10, 10), radius=3.2, color=self.accent_color)
        draw_hex_bolt(painter, QPointF(w - 10, 10), radius=3.2, color=self.accent_color)
        draw_hex_bolt(painter, QPointF(10, h - 10), radius=3.2, color=HUDColor.BORDER_DIM)
        draw_hex_bolt(painter, QPointF(w - 10, h - 10), radius=3.2, color=HUDColor.BORDER_DIM)

        # 5. 코너 네온 브래킷 액센트
        accent = HUDColor.RED if self.is_critical else self.accent_color
        painter.setPen(QPen(accent, 2.0))
        # 좌상단
        painter.drawLine(QPointF(0, cut + 8), QPointF(0, cut))
        painter.drawLine(QPointF(0, cut), QPointF(cut, 0))
        painter.drawLine(QPointF(cut, 0), QPointF(cut + 15, 0))
        # 우상단
        painter.drawLine(QPointF(w - cut - 15, 0), QPointF(w - cut, 0))
        painter.drawLine(QPointF(w - cut, 0), QPointF(w, cut))
        painter.drawLine(QPointF(w, cut), QPointF(w, cut + 8))
        # 좌하단
        painter.drawLine(QPointF(0, h - cut - 8), QPointF(0, h - cut))
        painter.drawLine(QPointF(0, h - cut), QPointF(cut, h))
        painter.drawLine(QPointF(cut, h), QPointF(cut + 15, h))
        # 우하단
        painter.drawLine(QPointF(w - cut - 15, h), QPointF(w - cut, h))
        painter.drawLine(QPointF(w - cut, h), QPointF(w, h - cut))
        painter.drawLine(QPointF(w, h - cut), QPointF(w, h - cut - 8))

        # 6. 헤더 텍스트 드로잉
        painter.setFont(get_font_mono(9, bold=True))
        painter.setPen(QPen(accent))
        painter.drawText(QRectF(22, 2, w - 180, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.title_text)

        # 7. 상태 태그 & LED 점
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.TEXT_MUTED))
        painter.drawText(QRectF(w - 160, 2, 130, 22), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, self.tag_text)

        led_color = HUDColor.RED if self.is_critical else HUDColor.GREEN
        painter.setBrush(QBrush(led_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(w - 22, 13), 3.5, 3.5)
        # LED 글로우
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(HUDColor.GREEN_GLOW if not self.is_critical else HUDColor.RED_GLOW, 2.0))
        painter.drawEllipse(QPointF(w - 22, 13), 5.5, 5.5)
