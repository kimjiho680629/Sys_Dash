"""
화이트 PCB AIDA64 스타일 상위 프로세스 HUD 테이블 위젯
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from theme import WhitePCBColor, get_font_bold, get_font_regular


class TopProcessTable(QWidget):
    """화이트 PCB 스타일 상위 5개 프로세스 테이블"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.procs = []
        self.setFixedHeight(105)

    def set_processes(self, procs):
        self.procs = procs[:5]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())

        row_h = 17.0
        header_y = 0.0

        # 헤더 배경
        painter.setBrush(QBrush(WhitePCBColor.BAR_BG))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.0))
        painter.drawRect(QRectF(1, header_y, w - 2, row_h))

        # 헤더 텍스트
        painter.setFont(get_font_bold(8))
        painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
        painter.drawText(QRectF(6, header_y, 42, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "PID")
        painter.drawText(QRectF(52, header_y, w - 160, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "NAME")
        painter.drawText(QRectF(w - 105, header_y, 48, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "CPU%")
        painter.drawText(QRectF(w - 52, header_y, 45, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "MEM%")

        # 데이터 행
        painter.setFont(get_font_regular(8))
        for i, proc in enumerate(self.procs):
            ry = header_y + row_h + (i * row_h)
            if ry + row_h > h:
                break

            # 교차 행 배경
            if i % 2 == 1:
                painter.setBrush(QBrush(QColor(245, 246, 249)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(1, ry, w - 2, row_h))

            # PID
            painter.setPen(QPen(WhitePCBColor.TEXT_MUTED))
            painter.drawText(QRectF(6, ry, 42, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(proc.get('pid', '')))

            # Name
            painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
            painter.drawText(QRectF(52, ry, w - 160, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(proc.get('name', '')))

            # CPU%
            cpu_val = proc.get('cpu_percent', 0.0)
            if cpu_val > 50:
                painter.setPen(QPen(QColor(220, 20, 60)))
            elif cpu_val > 15:
                painter.setPen(QPen(QColor(180, 100, 0)))
            else:
                painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
            painter.drawText(QRectF(w - 105, ry, 48, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{cpu_val:.1f}%")

            # MEM%
            mem_val = proc.get('mem_percent', 0.0)
            painter.setPen(QPen(WhitePCBColor.TEXT_SUB))
            painter.drawText(QRectF(w - 52, ry, 45, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{mem_val:.1f}%")
