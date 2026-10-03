"""
화이트 PCB 회로 기판 AIDA64 센서 패널 테마 정의
배경 회로 트레이스, 오프화이트 패널, 챠콜 테두리, 컴포넌트 아이콘 색상
"""

import math
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPolygonF, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF

class WhitePCBColor:
    # 배경 및 패널
    BG_BASE = QColor(235, 237, 241)        # 전체 바깥 배경
    BG_PANEL = QColor(255, 255, 255)       # 메인 화이트 패널
    BG_CARD = QColor(248, 249, 251)        # 내부 카드 서브 배경
    
    # 테두리 및 라인
    BORDER_MAIN = QColor(42, 45, 54)       # 진한 챠콜/블랙 메인 테두리
    BORDER_LIGHT = QColor(205, 210, 218)   # 연한 구분선
    GRID_LINE = QColor(215, 220, 228)      # 미니 그래프 그리드선
    PCB_TRACE = QColor(220, 224, 232)      # PCB 회로 트레이스 라인
    PCB_VIA = QColor(195, 202, 214)        # PCB 비아 홀 원형 패드

    # 텍스트
    TEXT_MAIN = QColor(30, 33, 42)          # 진한 블랙 텍스트
    TEXT_SUB = QColor(70, 75, 86)          # 보조 텍스트
    TEXT_MUTED = QColor(135, 142, 155)     # 연한 텍스트
    
    # 게이지 & 프로그레스 바
    BAR_FILL = QColor(58, 62, 74)          # 레퍼런스의 챠콜 그레이 채움 바
    BAR_BG = QColor(238, 240, 244)         # 바 배경 슬롯

    # 아이콘 & 액센트
    CHIP_BLUE_TOP = QColor(58, 123, 213)   # CPU 온도 칩셋 블루 상단
    CHIP_PURPLE_BOT = QColor(105, 48, 195) # CPU 온도 칩셋 퍼플 하단
    GPU_ACCENT = QColor(140, 60, 240)      # GPU RGB 액센트 (X자형)
    RAM_RGB_1 = QColor(0, 150, 255)
    RAM_RGB_2 = QColor(130, 0, 255)
    RAM_RGB_3 = QColor(255, 0, 128)
    WATER_DROP = QColor(45, 50, 62)        # 수온 물방울 다크 그레이
    VRM_CHIP = QColor(50, 55, 68)          # VRM 칩셋 다크 그레이


def get_font_bold(size=10):
    font = QFont("JetBrains Mono", size)
    if not font.exactMatch():
        font = QFont("FiraCode Nerd Font", size)
    if not font.exactMatch():
        font = QFont("Sans-Serif", size)
    font.setBold(True)
    return font


def get_font_regular(size=9):
    font = QFont("JetBrains Mono", size)
    if not font.exactMatch():
        font = QFont("FiraCode Nerd Font", size)
    if not font.exactMatch():
        font = QFont("Sans-Serif", size)
    font.setBold(False)
    return font


def draw_pcb_background(painter: QPainter, rect: QRectF):
    """
    레퍼런스 이미지와 동일한 PCB 회로 기판(Circuit Board) 트레이스 라인과 비아 패턴 절차적 렌더링
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 기본 화이트 배경
    painter.fillRect(rect, WhitePCBColor.BG_BASE)

    pen_trace = QPen(WhitePCBColor.PCB_TRACE, 1.8)
    pen_trace.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_trace)

    w = rect.width()
    h = rect.height()

    # 규칙적인 회로 트레이스 및 45도 꺾임 라인
    step_y = 65.0
    for y in range(20, int(h), int(step_y)):
        fy = float(y)
        # 가로선 -> 45도 꺾임 -> 가로선
        path = QPainterPath()
        path.moveTo(0, fy)
        path.lineTo(w * 0.25, fy)
        path.lineTo(w * 0.32, fy + 24)
        path.lineTo(w * 0.65, fy + 24)
        path.lineTo(w * 0.72, fy)
        path.lineTo(w, fy)
        painter.drawPath(path)

        # 역방향 라인
        path2 = QPainterPath()
        path2.moveTo(w, fy + 35)
        path2.lineTo(w * 0.78, fy + 35)
        path2.lineTo(w * 0.73, fy + 15)
        path2.lineTo(w * 0.45, fy + 15)
        path2.lineTo(w * 0.40, fy + 35)
        path2.lineTo(0, fy + 35)
        painter.drawPath(path2)

    # 비아 홀 (Via Pads: 동그란 단자 패드)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(WhitePCBColor.PCB_VIA))
    for x in range(40, int(w), 120):
        for y in range(30, int(h), 70):
            painter.drawEllipse(QPointF(x, y), 3.0, 3.0)
            painter.drawEllipse(QPointF(x + 50, y + 25), 2.2, 2.2)

    painter.restore()
