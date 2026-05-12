from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen

class ScanLineUI(QWidget):
    # 커스텀 시그널: 창의 좌표나 크기가 변할 때 발생
    region_changed = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.margin = 15
        self.dragging = False
        self.resizing_left = False
        self.resizing_right = False
        self.drag_position = QPoint()

        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setGeometry(100, 200, 800, 100)

    # --- UI 이벤트 발생 시 Signal 발송 ---
    def moveEvent(self, event):
        super().moveEvent(event)
        self.region_changed.emit(self.x(), self.y(), self.width(), self.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.region_changed.emit(self.x(), self.y(), self.width(), self.height())

    # --- 그리기 및 마우스 조작 (이전과 동일) ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.rect().width(), self.rect().height()
        mid_y = height // 2

        painter.setBrush(QColor(0, 255, 0, 30))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        painter.setPen(QPen(QColor(0, 255, 0, 255), 2))
        painter.drawLine(0, mid_y, width, mid_y)

        painter.setPen(QPen(QColor(0, 200, 0, 150), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, width - 1, height - 1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            if x < self.margin: self.resizing_left = True
            elif x > self.width() - self.margin: self.resizing_right = True
            else:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        if not (self.dragging or self.resizing_left or self.resizing_right):
            if x < self.margin or x > self.width() - self.margin: self.setCursor(Qt.SizeHorCursor)
            else: self.setCursor(Qt.SizeAllCursor)
        
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
        elif self.resizing_right:
            self.resize(event.pos().x(), self.height())
        elif self.resizing_left:
            dx = event.pos().x()
            self.setGeometry(self.x() + dx, self.y(), self.width() - dx, self.height())
        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing_left = False
        self.resizing_right = False
        self.setCursor(Qt.ArrowCursor)
        event.accept()