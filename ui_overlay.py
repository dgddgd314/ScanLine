import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QPen

class ScanLineUI(QWidget):
    def __init__(self):
        super().__init__()
        
        # UI 상태 변수
        self.margin = 15  # 마우스로 양 끝을 잡을 수 있는 여유 공간(px)
        self.dragging = False
        self.resizing_left = False
        self.resizing_right = False
        self.drag_position = QPoint()

        self.initUI()

    def initUI(self):
        # 1. 윈도우 속성 설정: 항상 위, 프레임 숨김, 작업표시줄 아이콘 숨김
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        
        # 2. 배경 완전히 투명하게 설정
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 3. 마우스 호버 이벤트를 실시간으로 받기 위해 트래킹 켜기
        self.setMouseTracking(True)
        
        # 4. 초기 크기 및 위치 (x, y, width, height)
        # height를 100으로 설정하여 캡처 엔진의 '버퍼 존' 크기와 맞춤
        self.setGeometry(100, 200, 800, 100)

    def paintEvent(self, event):
        """화면에 초록색 선과 캡처 영역(버퍼 존)을 그리는 함수"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.rect().width()
        height = self.rect().height()
        mid_y = height // 2

        # [버퍼 존] 전체 캡처 영역을 옅은 반투명 초록색으로 표시
        painter.setBrush(QColor(0, 255, 0, 30))  # 투명도 30
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # [기준선] 가운데에 선명한 초록색 가로선 그리기
        pen = QPen(QColor(0, 255, 0, 255), 2)  # 두께 2px
        painter.setPen(pen)
        painter.drawLine(0, mid_y, width, mid_y)

        # [테두리] 영역을 명확히 보여주기 위한 점선 테두리
        border_pen = QPen(QColor(0, 200, 0, 150), 1, Qt.DashLine)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(0, 0, width - 1, height - 1)

    # --- 마우스 조작 로직 ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x = event.pos().x()
            # 마우스가 왼쪽 끝에 있는지, 오른쪽 끝에 있는지, 가운데 있는지 판별
            if x < self.margin:
                self.resizing_left = True
            elif x > self.width() - self.margin:
                self.resizing_right = True
            else:
                self.dragging = True
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        x = event.pos().x()
        
        # 1. 마우스 커서 모양 변경 (호버 상태)
        if not (self.dragging or self.resizing_left or self.resizing_right):
            if x < self.margin or x > self.width() - self.margin:
                self.setCursor(Qt.SizeHorCursor) # 양 옆 화살표
            else:
                self.setCursor(Qt.SizeAllCursor) # 십자 화살표
        
        # 2. 실제 드래그 및 리사이즈 동작
        if self.dragging:
            self.move(event.globalPos() - self.drag_position)
        elif self.resizing_right:
            self.resize(event.pos().x(), self.height())
        elif self.resizing_left:
            dx = event.pos().x()
            # 왼쪽으로 늘리거나 줄일 때는 창의 x좌표와 width를 동시에 계산해야 함
            self.setGeometry(self.x() + dx, self.y(), self.width() - dx, self.height())
            
        event.accept()

    def mouseReleaseEvent(self, event):
        # 마우스 버튼을 놓으면 모든 상태 초기화
        self.dragging = False
        self.resizing_left = False
        self.resizing_right = False
        self.setCursor(Qt.ArrowCursor)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ScanLineUI()
    ex.show()
    sys.exit(app.exec_())