from PySide6.QtCore import Qt, QTimer, QSize, QRect, QPointF
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPainterPath,
    QFont,
    QPen,
    QTextOption,
    QFontMetrics,
    QLinearGradient,
)

class SpeechBubble(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(
            Qt.ToolTip | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.current_text = ""

        self.bg_color_top = QColor("#3AA0FF")
        self.bg_color_bottom = QColor("#1F86F5")
        self.text_color = QColor("#FFFFFF")
        self.border_color = QColor(255, 255, 255, 18)

        self.font_family = "Microsoft YaHei"
        self.font_size = 14
        self._font = QFont(self.font_family, self.font_size)
        self.setFont(self._font)

        self.padding_h = 16
        self.padding_v = 13
        self.border_radius = 18
        
        self.tail_width = 14
        self.tail_height = 12
        self.max_text_width = 180
        self.tail_left_offset = 25

        self.shadow_offset_x = 0
        self.shadow_offset_y = 6

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.hide_message)

        self.hide()

    def set_theme(self, bg_color=None, bg_color_top=None, bg_color_bottom=None, text_color=None, border_color=None, font_family=None, font_size=None):
        if bg_color is not None:
            color = QColor(bg_color) if not isinstance(bg_color, QColor) else bg_color
            self.bg_color_top = QColor(color)
            self.bg_color_bottom = QColor(color)
        if bg_color_top is not None:
            self.bg_color_top = QColor(bg_color_top) if not isinstance(bg_color_top, QColor) else bg_color_top
        if bg_color_bottom is not None:
            self.bg_color_bottom = QColor(bg_color_bottom) if not isinstance(bg_color_bottom, QColor) else bg_color_bottom
        if text_color is not None:
            self.text_color = QColor(text_color) if not isinstance(text_color, QColor) else text_color
        if border_color is not None:
            self.border_color = QColor(border_color) if not isinstance(border_color, QColor) else border_color
        if font_family is not None:
            self.font_family = font_family
        if font_size is not None:
            self.font_size = font_size

        self._font = QFont(self.font_family, self.font_size)
        self.setFont(self._font)
        self.updateGeometry()
        self.update()

    def set_incoming_style(self):
        self.set_theme(bg_color_top="#34363B", bg_color_bottom="#2B2D31", text_color="#F5F7FA", border_color=QColor(255, 255, 255, 14))

    def set_outgoing_blue_style(self):
        self.set_theme(bg_color_top="#3AA0FF", bg_color_bottom="#1F86F5", text_color="#FFFFFF", border_color=QColor(255, 255, 255, 16))

    def set_outgoing_green_style(self):
        self.set_theme(bg_color_top="#43D86B", bg_color_bottom="#2FC85A", text_color="#FFFFFF", border_color=QColor(255, 255, 255, 16))

    def show_message(self, pos, text, ms=3200):
        self.current_text = text or ""
        self.resize(self.sizeHint())
        self.move(pos)
        self.show()
        self.raise_()
        self.update()
        self._hide_timer.stop()
        self._hide_timer.start(ms)

    def hide_message(self):
        self.current_text = ""
        self.hide()

    def reposition(self, pos):
        if self.isVisible():
            self.move(pos)

    def _content_rect(self):
        return self.rect().adjusted(10, 10, -10, -15)

    def _bubble_rect(self):
        rect = self._content_rect()
        return QRect(
            rect.left(),
            rect.top(),
            rect.width(),
            max(0, rect.height() - self.tail_height),
        )

    def _text_rect(self):
        bubble_rect = self._bubble_rect()
        return QRect(
            bubble_rect.left() + self.padding_h,
            bubble_rect.top() + self.padding_v,
            max(0, bubble_rect.width() - self.padding_h * 2),
            max(0, bubble_rect.height() - self.padding_v * 2),
        )

    def _tail_points(self, dx=0, dy=0):
        bubble_rect = self._bubble_rect()
        
        base_x = bubble_rect.left() + self.tail_left_offset
        y_bottom = bubble_rect.bottom() - 1
        
        p1 = QPointF(base_x + self.tail_width, y_bottom)
        p2 = QPointF(base_x + self.tail_width * 0.3, y_bottom)
        p3 = QPointF(base_x - 4, y_bottom + self.tail_height)
        
        if dx != 0 or dy != 0:
            p1 += QPointF(dx, dy)
            p2 += QPointF(dx, dy)
            p3 += QPointF(dx, dy)
            
        return p1, p2, p3

    def _get_path(self, dx=0, dy=0):
        bubble_rect = self._bubble_rect().translated(dx, dy)
        left, top, right, bottom = bubble_rect.left(), bubble_rect.top(), bubble_rect.right(), bubble_rect.bottom()
        r = self.border_radius
        p1, p2, p3 = self._tail_points(dx, dy)

        path = QPainterPath()
        path.moveTo(left + r, top)
        path.lineTo(right - r, top)
        path.quadTo(right, top, right, top + r)
        path.lineTo(right, bottom - r)
        path.quadTo(right, bottom, right - r, bottom)
        
        path.lineTo(p1.x(), bottom)
        path.lineTo(p3.x(), p3.y())
        path.lineTo(p2.x(), bottom)
        
        path.lineTo(left + r, bottom)
        path.quadTo(left, bottom, left, bottom - r)
        path.lineTo(left, top + r)
        path.quadTo(left, top, left + r, top)
        path.closeSubpath()
        return path

    def paintEvent(self, event):
        if not self.current_text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 15))
        painter.drawPath(self._get_path(self.shadow_offset_x, self.shadow_offset_y + 1))

        path = self._get_path()
        bubble_rect = self._bubble_rect()
        gradient = QLinearGradient(bubble_rect.topLeft(), bubble_rect.bottomLeft())
        gradient.setColorAt(0.0, self.bg_color_top)
        gradient.setColorAt(1.0, self.bg_color_bottom)

        painter.setBrush(gradient)
        painter.drawPath(path)

        painter.setFont(self._font)
        painter.setPen(self.text_color)
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        option.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        painter.drawText(self._text_rect(), self.current_text, option)

    def sizeHint(self):
        text = self.current_text if self.current_text else " "
        fm = QFontMetrics(self._font)
        text_rect = fm.boundingRect(
            0, 0, self.max_text_width, 2000,
            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop,
            text,
        )

        width = text_rect.width() + self.padding_h * 2 + 25
        height = text_rect.height() + self.padding_v * 2 + self.tail_height + 25
        return QSize(max(width, 90), max(height, 50 + self.tail_height))