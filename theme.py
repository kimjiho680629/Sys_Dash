"""
화이트 & 다크 매트 PCB 회로 기판 AIDA64 센서 패널 테마 시스템
배경 회로 트레이스, 전류 펄스 애니메이션, 챠콜/옵시디언 패널, 컴포넌트 아이콘 색상
"""

import math
from PyQt6.QtGui import QColor, QFont, QPainter, QPen, QBrush, QPolygonF, QPainterPath
from PyQt6.QtCore import Qt, QPointF, QRectF
from config import Config


class WhiteThemeColors:
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
    PCB_PULSE = QColor(0, 150, 240, 200)   # PCB 전류 신호 펄스 빛

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
    
    # 추가 요소
    GRAPH_BG = QColor(255, 255, 255)
    TABLE_ROW_ALT = QColor(245, 246, 249)


class DarkThemeColors:
    # 배경 및 패널 (하이엔드 매트 블랙 / 옵시디언 PCB)
    BG_BASE = QColor(13, 15, 20)           # 딥 옵시디언 블랙 바깥 배경
    BG_PANEL = QColor(20, 23, 31)          # 메인 다크 아머 패널
    BG_CARD = QColor(26, 30, 41)           # 내부 카드 서브 배경
    
    # 테두리 및 라인
    BORDER_MAIN = QColor(50, 58, 76)       # 정밀 가공 슬레이트 메탈 테두리
    BORDER_LIGHT = QColor(34, 40, 54)      # 다크 서브 구분선
    GRID_LINE = QColor(32, 38, 52)         # 미니 그래프 그리드선
    PCB_TRACE = QColor(28, 33, 46)         # PCB 다크 트레이스 배선
    PCB_VIA = QColor(48, 58, 80)           # PCB 비아 홀 단자
    PCB_PULSE = QColor(0, 230, 255, 220)   # 다크에서 눈부신 일렉트릭 사이안 전류 펄스

    # 텍스트
    TEXT_MAIN = QColor(240, 244, 250)      # 선명한 고대비 화이트
    TEXT_SUB = QColor(165, 175, 195)       # 실버 그레이 보조 텍스트
    TEXT_MUTED = QColor(105, 115, 135)     # 차분한 슬레이트 뮤트 텍스트
    
    # 게이지 & 프로그레스 바
    BAR_FILL = QColor(0, 195, 255)         # 가독성과 사이버 감성의 네온 사이안 채움 바
    BAR_BG = QColor(28, 33, 45)            # 바 배경 슬롯

    # 아이콘 & 액센트
    CHIP_BLUE_TOP = QColor(30, 144, 255)   # CPU 온도 칩셋 네온 블루
    CHIP_PURPLE_BOT = QColor(147, 51, 234) # CPU 온도 칩셋 네온 퍼플
    GPU_ACCENT = QColor(168, 85, 247)      # GPU RGB 네온 바이올렛
    RAM_RGB_1 = QColor(0, 210, 255)
    RAM_RGB_2 = QColor(168, 85, 247)
    RAM_RGB_3 = QColor(244, 63, 94)
    WATER_DROP = QColor(28, 54, 88)        # 딥 네이비 물방울
    VRM_CHIP = QColor(32, 38, 50)          # 다크 모스펫 칩
    
    # 추가 요소
    GRAPH_BG = QColor(16, 19, 26)
    TABLE_ROW_ALT = QColor(25, 29, 39)


class ThemeManager:
    """
    글로벌 테마 상태 관리자
    """
    LIGHT = "light"
    DARK = "dark"
    
    _current_theme = getattr(Config, "DEFAULT_THEME", "dark").lower()
    _listeners = []

    @classmethod
    def get_theme(cls):
        return cls._current_theme

    @classmethod
    def set_theme(cls, theme_name):
        theme_name = theme_name.lower()
        if theme_name in (cls.LIGHT, cls.DARK) and cls._current_theme != theme_name:
            cls._current_theme = theme_name
            cls._notify_listeners()

    @classmethod
    def toggle_theme(cls):
        next_theme = cls.LIGHT if cls._current_theme == cls.DARK else cls.DARK
        cls.set_theme(next_theme)
        return next_theme

    @classmethod
    def is_dark(cls):
        return cls._current_theme == cls.DARK

    @classmethod
    def register_listener(cls, callback):
        if callback not in cls._listeners:
            cls._listeners.append(callback)

    @classmethod
    def unregister_listener(cls, callback):
        if callback in cls._listeners:
            cls._listeners.remove(callback)

    @classmethod
    def _notify_listeners(cls):
        for listener in list(cls._listeners):
            try:
                listener()
            except Exception as e:
                print(f"[ThemeManager] Error updating listener: {e}")


class ThemeProxy:
    """
    현재 활성화된 테마의 색상을 동적으로 매핑 반환하는 프록시
    기존 WhitePCBColor.XXX 호출 코드와 100% 호환
    """
    def __getattr__(self, name):
        colors = DarkThemeColors if ThemeManager.is_dark() else WhiteThemeColors
        return getattr(colors, name, QColor(0, 0, 0))


# 전역 테마 접근자
Theme = ThemeProxy()
WhitePCBColor = Theme  # 레거시 100% 호환성 지원


def get_font_bold(size=10):
    font = QFont("FiraCode Nerd Font", size)
    font.setBold(True)
    return font


def get_font_regular(size=9):
    font = QFont("FiraCode Nerd Font", size)
    font.setBold(False)
    return font


def get_font_semibold(size=10):
    font = QFont("FiraCode Nerd Font", size)
    font.setWeight(QFont.Weight.DemiBold)
    return font


def draw_pcb_background(painter: QPainter, rect: QRectF, pulse_offset: float = 0.0):
    """
    화이트 및 다크 모드를 지원하며, 살아 숨쉬는 회로 전류 펄스(Signal Flow Pulse)를
    렌더링하는 고성능 절차적 PCB 회로 기판 렌더러
    """
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # 1. 기판 기본 배경색 채우기
    painter.fillRect(rect, Theme.BG_BASE)

    w = rect.width()
    h = rect.height()

    # 2. PCB 회로 기본 트레이스 라인
    pen_trace = QPen(Theme.PCB_TRACE, 1.8)
    pen_trace.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen_trace)

    step_y = 65.0
    paths = []
    
    # 순방향 및 역방향 트레이스 경로 생성
    for y in range(20, int(h), int(step_y)):
        fy = float(y)
        
        # 가로선 -> 45도 꺾임 -> 가로선
        p1 = QPainterPath()
        p1.moveTo(0, fy)
        p1.lineTo(w * 0.25, fy)
        p1.lineTo(w * 0.32, fy + 24)
        p1.lineTo(w * 0.65, fy + 24)
        p1.lineTo(w * 0.72, fy)
        p1.lineTo(w, fy)
        painter.drawPath(p1)
        paths.append((p1, fy, 1))

        # 역방향 라인
        p2 = QPainterPath()
        p2.moveTo(w, fy + 35)
        p2.lineTo(w * 0.78, fy + 35)
        p2.lineTo(w * 0.73, fy + 15)
        p2.lineTo(w * 0.45, fy + 15)
        p2.lineTo(w * 0.40, fy + 35)
        p2.lineTo(0, fy + 35)
        painter.drawPath(p2)
        paths.append((p2, fy + 35, -1))

    # 3. 비아 홀 (Via Pads: 동그란 단자 패드)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(Theme.PCB_VIA))
    for x in range(40, int(w), 120):
        for y in range(30, int(h), 70):
            painter.drawEllipse(QPointF(x, y), 3.0, 3.0)
            painter.drawEllipse(QPointF(x + 50, y + 25), 2.2, 2.2)

    # 4. 살아 흐르는 PCB 회로 전류 신호 펄스 (Signal Flow Pulse Animation)
    # pulse_offset (0.0 ~ 1.0)에 따라 회로 선 위를 따라 빛의 점과 잔상이 흐름
    if pulse_offset >= 0.0:
        pulse_color = Theme.PCB_PULSE
        # 펄스 헤드 및 글로우
        glow_pen = QPen(pulse_color, 2.8)
        glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(glow_pen)

        for p, base_y, direction in paths:
            length = p.length()
            if length <= 0:
                continue

            # 라인마다 약간씩 다른 위상을 주어 자연스러운 분산 펄스 연출
            phase_shift = (base_y * 0.005)
            line_pct = (pulse_offset + phase_shift) % 1.0
            if direction < 0:
                line_pct = 1.0 - line_pct

            # 현재 펄스 위치
            pt_head = p.pointAtPercent(line_pct)
            painter.drawEllipse(pt_head, 2.2, 2.2)

            # 약간의 잔상(Tail) 펄스
            tail_pct = max(0.0, min(1.0, line_pct - (0.04 * direction)))
            pt_tail = p.pointAtPercent(tail_pct)
            tail_color = QColor(pulse_color)
            tail_color.setAlpha(int(tail_color.alpha() * 0.4))
            painter.setPen(QPen(tail_color, 1.8))
            painter.drawLine(pt_tail, pt_head)

    painter.restore()
