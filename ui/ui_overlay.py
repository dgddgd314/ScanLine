import sys
import ctypes
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen

class ScanLineUI(QWidget):
    # 좌표 변경 시 캡처 엔진에 알릴 시그널
    region_changed = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        self.margin = 15
        self.dragging = False
        self.resizing_left = False
        self.resizing_right = False
        self.drag_position = QPoint()
        self.bg_opacity = 30

        self.initUI()

    def initUI(self):
        # 1. 윈도우 속성: 항상 위, 테두리 없음, 툴팁 형태(작업표시줄 제외)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.setGeometry(100, 200, 800, 100)

        # 2. Windows API: 캡처 대상에서 이 창을 제외 (유령 모드)
        if sys.platform == 'win32':
            hwnd = int(self.winId())
            # WDA_EXCLUDEFROMCAPTURE = 0x00000011
            ctypes.windll.user32.SetWindowDisplayAffinity(hwnd, 0x00000011)

    def set_opacity(self, value):
        """0~100 사이의 값을 받아 배경 투명도 업데이트"""
        self.bg_opacity = value
        self.update() # 화면을 다시 그리도록 강제 호출 (paintEvent 재실행)
        
    def reset_position(self):
        """제어판에서 초기화 버튼을 누르면 화면 중앙 근처로 원복"""
        self.setGeometry(100, 200, 800, 100)
   
    def set_geometry_from_panel(self, x, y, w, h):
        """제어판 스핀박스에서 좌표를 입력받아 창 크기 조절"""
        self.setGeometry(x, y, w, h)
            
    def moveEvent(self, event):
        super().moveEvent(event)
        self.region_changed.emit(self.x(), self.y(), self.width(), self.height())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.region_changed.emit(self.x(), self.y(), self.width(), self.height())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.rect().width(), self.rect().height()
        mid_y = height // 2

        # QColor의 알파값은 0~255 기준이므로 비율을 맞춰줍니다.
        if self.bg_opacity > 0:
            alpha = int((self.bg_opacity / 100) * 255)
            painter.setBrush(QColor(0, 255, 0, alpha))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())

        # 중앙 가로선 (이미지에는 안 찍힘)
        painter.setPen(QPen(QColor(0, 255, 0, 255), 2))
        painter.drawLine(0, mid_y, width, mid_y)

        # 외곽 점선
        painter.setPen(QPen(QColor(0, 200, 0, 150), 1, Qt.DashLine))
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, width - 1, height - 1)

    # --- 💡 마우스 조작 로직 (이동/리사이즈 통합) ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            # 1. 왼쪽 끝 드래그 시 -> 왼쪽 리사이즈 모드
            if x < self.margin:
                self.resizing_left = True
            # 2. 오른쪽 끝 드래그 시 -> 오른쪽 리사이즈 모드
            elif x > self.width() - self.margin:
                self.resizing_right = True
            # 3. 가운데 드래그 시 -> 이동 모드
            else:
                self.dragging = True
                # [중요] 클릭 시점의 전역 좌표와 창 좌상단 좌표의 차이(Offset) 저장
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        
        # 커서 모양 변경 로직
        if not (self.dragging or self.resizing_left or self.resizing_right):
            if x < self.margin or x > self.width() - self.margin:
                self.setCursor(Qt.SizeHorCursor)
            else:
                self.setCursor(Qt.SizeAllCursor)
        
        # 실제 동작 수행
        if self.dragging:
            # 현재 마우스 전역 위치에서 처음 저장한 Offset을 빼서 창을 이동
            self.move(event.globalPos() - self.drag_position)
        elif self.resizing_right:
            self.resize(event.pos().x(), self.height())
        elif self.resizing_left:
            dx = event.pos().x()
            new_x = self.x() + dx
            new_width = self.width() - dx
            if new_width > self.margin * 2: # 최소 너비 제한
                self.setGeometry(new_x, self.y(), new_width, self.height())
        event.accept()

    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.resizing_left = False
        self.resizing_right = False
        self.setCursor(Qt.ArrowCursor)
        event.accept()