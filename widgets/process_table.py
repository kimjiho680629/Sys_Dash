"""
상위 리소스 점유 프로세스 TOP 5 HUD 테이블 위젯
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from theme import HUDColor, get_font_mono


class TopProcessTable(QWidget):
    """TOP 5 프로세스 사이버펑크 HUD 리스트"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.procs = []
        self.setFixedHeight(120)

    def set_processes(self, procs):
        self.procs = procs[:5]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        row_h = 19.0
        header_y = 0.0

        # 헤더 배경
        painter.setBrush(QBrush(HUDColor.BG_CARD_LIGHT))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(0, header_y, w, row_h))

        # 헤더 텍스트
        painter.setFont(get_font_mono(8, bold=True))
        painter.setPen(QPen(HUDColor.CYAN_DIM))
        painter.drawText(QRectF(8, header_y, 45, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "PID")
        painter.drawText(QRectF(55, header_y, w - 170, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "NAME")
        painter.drawText(QRectF(w - 110, header_y, 50, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "CPU%")
        painter.drawText(QRectF(w - 55, header_y, 45, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "MEM%")

        # 데이터 행
        painter.setFont(get_font_mono(8))
        for i, proc in enumerate(self.procs):
            ry = header_y + row_h + (i * row_h)
            # 행 번갈아 배경 틴트
            if i % 2 == 1:
                painter.setBrush(QBrush(HUDColor.BG_CARD))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(0, ry, w, row_h))

            # PID
            painter.setPen(QPen(HUDColor.TEXT_MUTED))
            painter.drawText(QRectF(8, ry, 45, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(proc.get('pid', '')))

            # Name
            painter.setPen(QPen(HUDColor.TEXT_TITLE))
            painter.drawText(QRectF(55, ry, w - 170, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(proc.get('name', '')))

            # CPU%
            cpu_val = proc.get('cpu_percent', 0.0)
            if cpu_val > 50:
                painter.setPen(QPen(HUDColor.RED))
            elif cpu_val > 10:
                painter.setPen(QPen(HUDColor.AMBER))
            else:
                painter.setPen(QPen(HUDColor.CYAN))
            painter.drawText(QRectF(w - 110, ry, 50, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{cpu_val:.1f}%")

            # MEM%
            mem_val = proc.get('mem_percent', 0.0)
            painter.setPen(QPen(HUDColor.TEXT_BODY))
            painter.drawText(QRectF(w - 55, ry, 45, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{mem_val:.1f}%")
