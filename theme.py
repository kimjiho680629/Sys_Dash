"""
사이버펑크 SF 하이테크 & 슈퍼카 센서 클러스터 테마
팔레트, 폰트, 헥사곤 메쉬 및 메카닉 볼트 드로잉 유틸리티
"""

import math
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPolygonF
from PyQt6.QtCore import Qt, QPointF, QRectF

class HUDColor:
    # 딥 스페이스 배경
    BG_VOID = QColor(5, 8, 15)            # 극암청색
    BG_PANEL = QColor(10, 15, 28, 240)    # 반투명 HUD 패널
    BG_CARD = QColor(14, 22, 40, 220)     # 카드 내부
    BG_CARD_LIGHT = QColor(22, 34, 58, 200)
    BG_CORE_BLOCK = QColor(16, 26, 48, 230) # 실리콘 코어 블록

    # 네온 액센트
    CYAN = QColor(0, 240, 255)            # 메인 네온 시안
    CYAN_GLOW = QColor(0, 240, 255, 60)
    CYAN_DIM = QColor(0, 160, 180, 150)
    
    MAGENTA = QColor(255, 0, 128)         # 서브 네온 마젠타
    MAGENTA_GLOW = QColor(255, 0, 128, 60)
    
    PURPLE = QColor(157, 78, 221)         # 딥 일렉트릭 퍼플
    PURPLE_GLOW = QColor(157, 78, 221, 60)
    
    GREEN = QColor(0, 255, 157)           # 레이싱 에메랄드 그린
    GREEN_GLOW = QColor(0, 255, 157, 60)
    
    GOLD = QColor(255, 195, 0)            # 슈퍼카 골드 앰버
    GOLD_GLOW = QColor(255, 195, 0, 70)
    AMBER = QColor(255, 190, 11)          # 워닝 앰버
    
    RED = QColor(255, 42, 85)             # 크리티컬 레드
    RED_GLOW = QColor(255, 42, 85, 90)

    # 텍스트 & 라인
    TEXT_TITLE = QColor(240, 250, 255)
    TEXT_BODY = QColor(185, 215, 240)
    TEXT_SECONDARY = QColor(130, 175, 210)
    TEXT_MUTED = QColor(75, 110, 145)
    
    GRID_LINE = QColor(22, 38, 65, 100)
    HEX_GRID = QColor(18, 30, 52, 70)
    BORDER_HUD = QColor(0, 240, 255, 110)
    BORDER_DIM = QColor(35, 60, 95, 130)


def get_font_mono(size=10, bold=False):
    """Monospace 코드 및 데이터 폰트 (JetBrains Mono 우선)"""
    font = QFont("JetBrains Mono", size)
    if not font.exactMatch():
        font = QFont("FiraCode Nerd Font", size)
    if not font.exactMatch():
        font = QFont("Monospace", size)
    font.setBold(bold)
    return font


def get_font_display(size=14, bold=True):
    """헤더 및 대형 디지털 수치용 디스플레이 폰트"""
    font = QFont("JetBrains Mono", size)
    if not font.exactMatch():
        font = QFont("FiraCode Nerd Font", size)
    font.setBold(bold)
    return font


def draw_hex_bolt(painter: QPainter, center: QPointF, radius: float = 4.0, color: QColor = HUDColor.BORDER_DIM):
    """사이버네틱 패널 코너의 육각 볼트 마킹 드로잉"""
    pts = []
    for i in range(6):
        rad = math.radians(60 * i)
        pts.append(QPointF(center.x() + radius * math.cos(rad), center.y() + radius * math.sin(rad)))
    painter.setPen(QPen(color, 1.0))
    painter.setBrush(QBrush(HUDColor.BG_VOID))
    painter.drawPolygon(QPolygonF(pts))
    # 중앙 홈
    painter.drawPoint(center)


def draw_hexagon_mesh(painter: QPainter, rect: QRectF, side: float = 16.0):
    """배경에 은은한 벌집(Hexagon Mesh) 사이버네틱 패턴 렌더링"""
    painter.save()
    painter.setPen(QPen(HUDColor.HEX_GRID, 0.8))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    w = rect.width()
    h = rect.height()
    dx = side * 1.5
    dy = side * math.sqrt(3)

    cols = int(w / dx) + 2
    rows = int(h / dy) + 2

    for col in range(cols):
        for row in range(rows):
            cx = rect.left() + col * dx
            cy = rect.top() + row * dy + (dy / 2.0 if col % 2 else 0)
            pts = []
            for i in range(6):
                rad = math.radians(60 * i)
                pts.append(QPointF(cx + side * 0.5 * math.cos(rad), cy + side * 0.5 * math.sin(rad)))
            painter.drawPolygon(QPolygonF(pts))
    painter.restore()
