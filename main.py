import sys
from PyQt5.QtWidgets import QApplication
from ui.ui_overlay import ScanLineUI
from core.capture_engine import CaptureThread

def main():
    app = QApplication(sys.argv)
    
    overlay_ui = ScanLineUI()
    capture_thread = CaptureThread(fps=5)
    overlay_ui.region_changed.connect(capture_thread.update_region)
    
    # 초기 상태 동기화 및 실행
    capture_thread.update_region(
        overlay_ui.x(), overlay_ui.y(), overlay_ui.width(), overlay_ui.height()
    )
    
    capture_thread.start()
    overlay_ui.show()
    
    app.aboutToQuit.connect(capture_thread.stop)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()