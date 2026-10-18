"""
화이트 & 다크 PCB AIDA64 스타일 상위 프로세스 HUD 테이블 위젯
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF
from theme import WhitePCBColor, ThemeManager, get_font_bold, get_font_regular


class TopProcessTable(QWidget):
    """화이트 & 다크 PCB 스타일 상위 7개 프로세스 센티넬 테이블 (CPU 점유율 내림차순)"""
    MAX_ROWS = 7

    def __init__(self, parent=None):
        super().__init__(parent)
        self.procs = []
        self.setMinimumHeight(148)
        ThemeManager.register_listener(self.update)

    def set_processes(self, procs):
        if procs:
            # UI 레벨에서도 CPU 점유율 내림차순 정렬 보장 및 상위 7개 유지 (Zero-Drop 보호)
            sorted_procs = sorted(
                procs,
                key=lambda x: (x.get('cpu_percent', 0.0) or 0.0, x.get('mem_percent', 0.0) or 0.0),
                reverse=True
            )
            self.procs = sorted_procs[:self.MAX_ROWS]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = ThemeManager.is_dark()

        header_y = 0.0
        header_h = 19.0
        avail_h = max(105.0, h - header_h - 2.0)
        row_h = min(19.5, avail_h / float(self.MAX_ROWS))

        # 헤더 배경
        painter.setBrush(QBrush(WhitePCBColor.BAR_BG))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.0))
        painter.drawRect(QRectF(1, header_y, w - 2, header_h))

        # 헤더 텍스트 (9.5pt Bold)
        painter.setFont(get_font_bold(9))
        painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
        painter.drawText(QRectF(6, header_y, 48, header_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "PID")
        painter.drawText(QRectF(56, header_y, w - 175, header_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "NAME")
        painter.drawText(QRectF(w - 116, header_y, 56, header_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "CPU% ▼")
        painter.drawText(QRectF(w - 55, header_y, 50, header_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "MEM%")

        # 데이터 행 (7개 전체 렌더링 보장)
        painter.setFont(get_font_regular(9))
        for i, proc in enumerate(self.procs[:self.MAX_ROWS]):
            ry = header_y + header_h + (i * row_h)

            # 교차 행 배경
            if i % 2 == 1:
                painter.setBrush(QBrush(WhitePCBColor.TABLE_ROW_ALT))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(QRectF(1, ry, w - 2, row_h))

            # PID
            painter.setPen(QPen(WhitePCBColor.TEXT_MUTED))
            painter.drawText(QRectF(6, ry, 46, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(proc.get('pid', '')))

            # Name
            painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
            painter.drawText(QRectF(54, ry, w - 165, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, str(proc.get('name', '')))

            # CPU% (임계값에 따른 경고 색상 강조)
            cpu_val = float(proc.get('cpu_percent', 0.0) or 0.0)
            if cpu_val > 50.0:
                painter.setPen(QPen(QColor(255, 60, 80) if is_dark else QColor(220, 20, 60)))
            elif cpu_val > 15.0:
                painter.setPen(QPen(QColor(255, 170, 0) if is_dark else QColor(180, 100, 0)))
            elif cpu_val > 0.0:
                painter.setPen(QPen(QColor(0, 230, 255) if is_dark else WhitePCBColor.TEXT_MAIN))
            else:
                painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
            painter.drawText(QRectF(w - 110, ry, 50, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{cpu_val:.1f}%")

            # MEM%
            mem_val = float(proc.get('mem_percent', 0.0) or 0.0)
            painter.setPen(QPen(WhitePCBColor.TEXT_SUB))
            painter.drawText(QRectF(w - 52, ry, 47, row_h), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, f"{mem_val:.1f}%")

