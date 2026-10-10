"""
화이트 & 다크 PCB AIDA64 센서 패널 전용 하드웨어 아이콘 컴포넌트
CPU 소켓 칩, GPU 그래픽카드, 수온 물방울, VRM 칩, XPG LANCER RGB DDR5, SSD, 쿨러 팬
생동감 넘치는 RGB 웨이브, 네온 브리딩 펄스, 팬 회전 애니메이션 내장
"""

import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QPainterPath, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from theme import WhitePCBColor, ThemeManager, get_font_bold, get_font_regular


class CpuSocketBadge(QWidget):
    """
    CPU 소켓 패키지 온도 아이콘
    상하좌우 핀(Pins), 내부 블루-퍼플 그라디언트 코어, 대형 흰색 온도 숫자, 미세 펄스 쉬머
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_c = 44.0
        self.pulse_phase = 0.0
        self.setFixedSize(96, 96)

        # 미세 펄스 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._pulse_tick)
        self.timer.start(50)

    def _pulse_tick(self):
        self.pulse_phase = (self.pulse_phase + 0.05) % (math.pi * 2)
        self.update()

    def set_temp(self, temp):
        self.temp_c = float(temp)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        cx = w / 2.0
        cy = h / 2.0

        is_dark = ThemeManager.is_dark()

        # 1. 외곽 핀 (Pins: 금색/은색 소켓 단자)
        pin_c = QColor(130, 140, 160) if is_dark else QColor(160, 165, 175)
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

        # 2. 메인 CPU 기판
        pkg_rect = QRectF(cx - 32, cy - 32, 64, 64)
        pkg_bg = QColor(26, 30, 42) if is_dark else QColor(42, 45, 54)
        pkg_border = QColor(16, 18, 26) if is_dark else QColor(25, 28, 35)
        painter.setBrush(QBrush(pkg_bg))
        painter.setPen(QPen(pkg_border, 2.0))
        painter.drawRoundedRect(pkg_rect, 4, 4)

        # 3. 내부 IHS / 코어 다이 (블루-퍼플 그라디언트 + 은은한 에너지 쉬머)
        core_rect = QRectF(cx - 24, cy - 24, 48, 48)
        grad = QLinearGradient(cx, cy - 24, cx, cy + 24)
        
        # 펄스 위상에 따른 미세 밝기 변화
        shimmer = int(15 * math.sin(self.pulse_phase))
        top_c = QColor(WhitePCBColor.CHIP_BLUE_TOP)
        top_c = QColor(min(255, max(0, top_c.red() + shimmer)),
                       min(255, max(0, top_c.green() + shimmer)),
                       min(255, max(0, top_c.blue() + shimmer)))
        bot_c = WhitePCBColor.CHIP_PURPLE_BOT

        grad.setColorAt(0.0, top_c)
        grad.setColorAt(0.55, top_c)
        grad.setColorAt(0.85, bot_c)
        grad.setColorAt(1.0, bot_c)

        painter.setBrush(QBrush(grad))
        border_glow = QColor(200, 240, 255, 240) if is_dark else QColor(255, 255, 255, 220)
        painter.setPen(QPen(border_glow, 1.8))
        painter.drawRoundedRect(core_rect, 3, 3)

        # 4. 중앙 대형 흰색 온도 숫자
        painter.setFont(get_font_bold(22))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(core_rect, Qt.AlignmentFlag.AlignCenter, str(int(round(self.temp_c))))


class GpuCardBadge(QWidget):
    """
    그래픽카드 외형 온도 아이콘
    좌측 대형 온도 숫자, 중앙 X자 네온 RGB 브리딩 액센트, 우측 회전 쿨링 팬
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_c = 43
        self.fan_angle = 0.0
        self.breathe_phase = 0.0
        self.setFixedSize(140, 52)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(30)

    def _on_tick(self):
        self.fan_angle = (self.fan_angle + 6.0) % 360
        self.breathe_phase = (self.breathe_phase + 0.06) % (math.pi * 2)
        self.update()

    def set_temp(self, temp):
        self.temp_c = int(round(temp))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = ThemeManager.is_dark()

        # 1. 그래픽카드 슈라우드 바디
        body_rect = QRectF(4, 4, w - 8, h - 8)
        body_bg = QColor(28, 33, 46) if is_dark else QColor(45, 48, 58)
        body_border = QColor(16, 19, 28) if is_dark else QColor(28, 30, 38)
        painter.setBrush(QBrush(body_bg))
        painter.setPen(QPen(body_border, 2.0))
        painter.drawRoundedRect(body_rect, 4, 4)

        # 2. 좌측 온도 표시 구역
        temp_rect = QRectF(10, 4, 42, h - 8)
        painter.setFont(get_font_bold(20))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(temp_rect, Qt.AlignmentFlag.AlignCenter, str(self.temp_c))

        # 3. 중앙 X자 네온 RGB 액센트 (호흡 Breathing Glow)
        mid_x = 72.0
        cy = h / 2.0
        breathe = (math.sin(self.breathe_phase) + 1.0) / 2.0  # 0.0 ~ 1.0
        accent_color = QColor(WhitePCBColor.GPU_ACCENT)
        alpha = int(160 + breathe * 95)
        accent_color.setAlpha(alpha)

        pen_width = 2.5 + breathe * 0.8
        painter.setPen(QPen(accent_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(mid_x - 14, cy - 14), QPointF(mid_x + 14, cy + 14))
        painter.drawLine(QPointF(mid_x - 14, cy + 14), QPointF(mid_x + 14, cy - 14))

        # 4. 우측 회전 쿨링 팬
        fx = w - 26.0
        fy = cy
        fr = 14.0

        ring_c = QColor(120, 130, 150) if is_dark else QColor(180, 185, 195)
        painter.setPen(QPen(ring_c, 1.2))
        painter.setBrush(QBrush(QColor(18, 21, 29) if is_dark else QColor(25, 28, 35)))
        painter.drawEllipse(QPointF(fx, fy), fr, fr)

        painter.save()
        painter.translate(fx, fy)
        painter.rotate(self.fan_angle)
        blade_c = QColor(0, 220, 255) if is_dark else Qt.GlobalColor.white
        blade_pen = QPen(blade_c, 2.0)
        painter.setPen(blade_pen)
        for i in range(5):
            painter.rotate(72)
            painter.drawLine(0, 0, 0, int(fr - 3))
        painter.restore()


class LiquidDropBadge(QWidget):
    """수온(Liquid Temp) 물방울 아이콘"""
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
        is_dark = ThemeManager.is_dark()

        path = QPainterPath()
        path.moveTo(cx, 6)
        path.cubicTo(cx + 28, 34, cx + 28, h - 8, cx, h - 8)
        path.cubicTo(cx - 28, h - 8, cx - 28, 34, cx, 6)

        painter.setBrush(QBrush(WhitePCBColor.WATER_DROP))
        border_c = QColor(0, 180, 255, 180) if is_dark else QColor(20, 22, 28)
        painter.setPen(QPen(border_c, 2.0))
        painter.drawPath(path)

        painter.setFont(get_font_bold(11))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(QRectF(0, 28, w, 32), Qt.AlignmentFlag.AlignCenter, f"{self.temp_c}°C")


class VrmChipBadge(QWidget):
    """전원부(VRM Temp) 모스펫 칩셋 아이콘"""
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
        is_dark = ThemeManager.is_dark()

        tab_poly = QPolygonF([
            QPointF(cx - 18, 6),
            QPointF(cx + 18, 6),
            QPointF(cx + 24, 18),
            QPointF(cx - 24, 18)
        ])
        tab_bg = QColor(100, 110, 130) if is_dark else QColor(180, 185, 195)
        tab_border = QColor(70, 80, 100) if is_dark else QColor(140, 145, 155)
        painter.setBrush(QBrush(tab_bg))
        painter.setPen(QPen(tab_border, 1.0))
        painter.drawPolygon(tab_poly)

        painter.setBrush(QBrush(QColor(30, 34, 46) if is_dark else QColor(60, 64, 75)))
        painter.drawEllipse(QPointF(cx, 12), 4.0, 4.0)

        body_rect = QRectF(cx - 24, 18, 48, 36)
        painter.setBrush(QBrush(WhitePCBColor.VRM_CHIP))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.5))
        painter.drawRoundedRect(body_rect, 2, 2)

        pin_c = QColor(110, 120, 140) if is_dark else QColor(160, 165, 175)
        painter.setPen(QPen(pin_c, 2.5))
        for px in [cx - 14, cx, cx + 14]:
            painter.drawLine(QPointF(px, 54), QPointF(px, 64))

        painter.setFont(get_font_bold(11))
        painter.setPen(QPen(Qt.GlobalColor.white))
        painter.drawText(body_rect, Qt.AlignmentFlag.AlignCenter, f"{self.temp_c}°C")


class XpgLancerBadge(QWidget):
    """
    ADATA XPG LANCER RGB DDR5 고유의 기하학적 알루미늄 방열판 +
    생동감 넘치는 실시간 네온 오로라 RGB 웨이브 애니메이션 (RGB Light Bar & 삼각 프리즘)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(44)
        self.rgb_phase = 0.0

        # RGB 웨이브 애니메이션 타이머 (30ms = 약 33 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rgb_tick)
        self.timer.start(30)

    def _rgb_tick(self):
        self.rgb_phase = (self.rgb_phase + 0.012) % 1.0
        self.update()

    def _get_wave_color(self, base_ratio):
        # 360도 색상 휠 기반의 부드러운 오로라 웨이브
        hue = int((base_ratio + self.rgb_phase) * 360.0) % 360
        # 채도와 명도를 게이밍 RGB 네온 감성에 최적화 (Saturation 230, Value 255)
        return QColor.fromHsv(hue, 230, 255)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = ThemeManager.is_dark()

        # 1. 상단 RGB 라이트 바 (살아 숨쉬며 흐르는 프리미엄 네온 오로라 웨이브)
        rgb_rect = QRectF(2, 4, w - 4, 10)
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, self._get_wave_color(0.0))
        grad.setColorAt(0.33, self._get_wave_color(0.33))
        grad.setColorAt(0.66, self._get_wave_color(0.66))
        grad.setColorAt(1.0, self._get_wave_color(1.0))

        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rgb_rect, 2, 2)

        # 2. XPG LANCER 시그니처: 우측 상단 삼각 프리즘 RGB 윈도우
        tri_rgb = QPolygonF([
            QPointF(w - 46, 12),
            QPointF(w - 2, 12),
            QPointF(w - 2, 28)
        ])
        tri_grad = QLinearGradient(w - 46, 12, w - 2, 28)
        tri_grad.setColorAt(0.0, self._get_wave_color(0.7))
        tri_grad.setColorAt(1.0, self._get_wave_color(0.95))
        painter.setBrush(QBrush(tri_grad))
        painter.drawPolygon(tri_rgb)

        # 3. 하단 XPG 다이캐스트 알루미늄 건메탈 방열판 바디
        sink_poly = QPolygonF([
            QPointF(2, 12),
            QPointF(w - 46, 12),
            QPointF(w - 2, 28),
            QPointF(w - 2, h - 3),
            QPointF(2, h - 3)
        ])
        sink_bg = QColor(24, 28, 38) if is_dark else QColor(36, 39, 48)
        sink_border = QColor(14, 16, 22) if is_dark else QColor(18, 20, 26)
        painter.setBrush(QBrush(sink_bg))
        painter.setPen(QPen(sink_border, 1.8))
        painter.drawPolygon(sink_poly)

        # 4. 방열판 내부 사선 메탈릭 헤어라인 엠보싱
        line_c1 = QColor(60, 70, 90) if is_dark else QColor(70, 75, 90)
        line_c2 = QColor(40, 48, 65) if is_dark else QColor(50, 54, 66)
        painter.setPen(QPen(line_c1, 1.5))
        painter.drawLine(QPointF(24, h - 6), QPointF(w - 60, 14))
        painter.setPen(QPen(line_c2, 1.2))
        painter.drawLine(QPointF(32, h - 6), QPointF(w - 52, 14))

        # 5. 좌측 XPG 양각 실버/화이트 로고 텍스트
        painter.setFont(get_font_bold(10))
        painter.setPen(QPen(QColor(240, 245, 255)))
        painter.drawText(QRectF(14, 16, 60, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "XPG")

        # 6. 우측 DDR5 서브 텍스트 배지
        painter.setFont(get_font_bold(8))
        painter.setPen(QPen(QColor(130, 140, 160) if is_dark else QColor(140, 145, 160)))
        painter.drawText(QRectF(w - 95, 20, 45, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "DDR5")


# 레거시 호환용 alias
TridentZBadge = XpgLancerBadge


class MotherboardBadge(QWidget):
    """
    기가바이트 B850I AORUS PRO 메인보드 전용 HUD 배지
    사선 아머 플레이트, 실시간 PCIe 데이터 버스 링크 펄스 애니메이션, BIOS 및 칩셋 스펙
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(58)
        self.board_name = "B850I AORUS PRO"
        self.vendor = "GIGABYTE"
        self.bios_ver = "F13c"
        self.chipset = "AMD B850"
        self.temp_c = 38
        self.bus_phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._bus_tick)
        self.timer.start(40)

        ThemeManager.register_listener(self.update)

    def _bus_tick(self):
        self.bus_phase = (self.bus_phase + 0.08) % (math.pi * 2)
        self.update()

    def set_data(self, mobo_data):
        if not mobo_data:
            return
        self.board_name = mobo_data.get("board_name", self.board_name)
        self.vendor = mobo_data.get("vendor", self.vendor)
        self.bios_ver = mobo_data.get("bios_ver", self.bios_ver)
        self.chipset = mobo_data.get("chipset", self.chipset)
        self.temp_c = int(round(mobo_data.get("temp_c", self.temp_c)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = ThemeManager.is_dark()
        cut = 10.0

        # 1. 사선 아머 베이스 플레이트
        poly = QPolygonF([
            QPointF(0, 0),
            QPointF(w - cut, 0),
            QPointF(w, cut),
            QPointF(w, h),
            QPointF(cut, h),
            QPointF(0, h - cut)
        ])
        body_bg = QColor(24, 28, 38) if is_dark else QColor(242, 244, 248)
        painter.setBrush(QBrush(body_bg))
        painter.setPen(QPen(WhitePCBColor.BORDER_MAIN, 1.8))
        painter.drawPolygon(poly)

        # 2. 좌측 주황색/사이안 액센트 세로 바
        accent_c = QColor(255, 110, 0) if not is_dark else QColor(0, 210, 255)
        painter.setBrush(QBrush(accent_c))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(4, 8, 3, h - 16))

        # 3. 메인보드 모델명 텍스트 (볼드 11pt)
        painter.setFont(get_font_bold(11))
        painter.setPen(QPen(WhitePCBColor.TEXT_MAIN))
        painter.drawText(QRectF(14, 6, w - 85, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"{self.vendor} {self.board_name}")

        # 4. 서브 스펙 (9pt)
        painter.setFont(get_font_regular(9))
        painter.setPen(QPen(WhitePCBColor.TEXT_MUTED))
        sub_info = f"BIOS: {self.bios_ver}  |  PCIe 5.0 x16  |  {self.chipset}"
        painter.drawText(QRectF(14, 28, w - 85, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, sub_info)

        # 5. 우측 버스 링크 펄스 LED 4개 (Data Link Pulse)
        rx = w - 75
        for i in range(4):
            px = rx + i * 14.0
            py = 16.0
            shift = (self.bus_phase - i * 0.8) % (math.pi * 2)
            intensity = (math.sin(shift) + 1.0) / 2.0
            led_c = QColor(0, int(180 + 75 * intensity), int(220 + 35 * intensity)) if is_dark else QColor(int(200 + 55 * intensity), 80, 0)
            painter.setBrush(QBrush(led_c))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(px, py), 2.5, 2.5)

        # 우측 하단 LINK 상태 텍스트
        painter.setFont(get_font_bold(8))
        link_c = QColor(0, 220, 255) if is_dark else QColor(255, 110, 0)
        painter.setPen(QPen(link_c))
        painter.drawText(QRectF(w - 78, 30, 68, 16), Qt.AlignmentFlag.AlignCenter, "LINK ACTIVE")


class AudioVuVisualizer(QWidget):
    """
    PipeWire 실시간 8밴드 점핑 VU 이퀄라이저 스펙트럼 위젯
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(96, 38)
        self.volume_pct = 30
        self.is_muted = False
        
        # 8밴드 VU 미터 시뮬레이션 상태값
        self.bands = [0.15] * 8
        self.peaks = [0.15] * 8
        self.vu_phase = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._vu_tick)
        self.timer.start(35)

        ThemeManager.register_listener(self.update)

    def _vu_tick(self):
        self.vu_phase = (self.vu_phase + 0.12) % (math.pi * 2)
        base_vol = 0.0 if self.is_muted else (self.volume_pct / 100.0)
        
        # 8개 밴드의 음악/사운드 리듬감 있는 점핑 애니메이션
        for i in range(8):
            wave = (math.sin(self.vu_phase * (1.2 + i * 0.3) + i * 0.7) + 1.0) * 0.5
            target_h = base_vol * (0.25 + wave * 0.75)
            self.bands[i] += (target_h - self.bands[i]) * 0.35

            if self.bands[i] > self.peaks[i]:
                self.peaks[i] = self.bands[i]
            else:
                self.peaks[i] = max(0.0, self.peaks[i] - 0.02)  # 피크 캡 서서히 하강

        self.update()

    def set_data(self, audio_data):
        if not audio_data:
            return
        self.volume_pct = audio_data.get("volume_percent", self.volume_pct)
        self.is_muted = audio_data.get("muted", False)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        is_dark = ThemeManager.is_dark()

        # 8밴드 실시간 점핑 VU 이퀄라이저 바
        band_w = 8.0
        spacing = 4.0
        total_w = 8 * band_w + 7 * spacing
        start_x = (w - total_w) / 2.0

        for i in range(8):
            bx = start_x + i * (band_w + spacing)
            bh = max(2.0, h * self.bands[i])
            by = h - bh

            # 바 그라디언트 (하단 사이안 -> 상단 마젠타/코랄)
            grad = QLinearGradient(bx, h, bx, 0)
            if is_dark:
                grad.setColorAt(0.0, QColor(0, 180, 255))
                grad.setColorAt(0.7, QColor(140, 60, 255))
                grad.setColorAt(1.0, QColor(255, 50, 100))
            else:
                grad.setColorAt(0.0, QColor(60, 70, 90))
                grad.setColorAt(0.7, QColor(90, 100, 130))
                grad.setColorAt(1.0, QColor(140, 50, 80))

            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(bx, by, band_w, bh))

            # 상단 피크 홀드 캡 (Peak Hold Cap)
            peak_y = h - max(2.0, h * self.peaks[i])
            cap_c = QColor(255, 230, 100) if is_dark else QColor(40, 45, 55)
            painter.setBrush(QBrush(cap_c))
            painter.drawRect(QRectF(bx, peak_y - 2, band_w, 2))
