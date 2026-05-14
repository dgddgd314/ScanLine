import sys
from PyQt5.QtWidgets import QApplication
from ui.ui_overlay import ScanLineUI
from ui.control_panel import ControlPanel
from core.capture_engine import CaptureThread

def main():
    app = QApplication(sys.argv)
    
    overlay_ui = ScanLineUI()
    control_panel = ControlPanel()
    capture_thread = CaptureThread(fps=5)

    # [UI <-> UI 연결]
    control_panel.opacity_changed.connect(overlay_ui.set_opacity)
    control_panel.reset_requested.connect(overlay_ui.reset_position)
    control_panel.geometry_changed.connect(overlay_ui.set_geometry_from_panel)
    overlay_ui.region_changed.connect(control_panel.update_geometry_spins)

    # [UI <-> 백그라운드 스레드 연결]
    overlay_ui.region_changed.connect(capture_thread.update_region)
    control_panel.fps_changed.connect(lambda fps: setattr(capture_thread, 'fps', fps))
    control_panel.scan_toggled.connect(capture_thread.set_capturing)
    control_panel.scan_toggled.connect(lambda is_on: control_panel.log_message(f"Scan Mode: {'ON' if is_on else 'OFF'}")) # TODO: 실제 스캔 모드 토글 기능은 나중에 구현 예정
    
    # 초기 상태 동기화 및 실행
    capture_thread.update_region(
        overlay_ui.x(), overlay_ui.y(), overlay_ui.width(), overlay_ui.height()
    )
    
    # 처음에 캡처 스레드는 바로 시작하지 않고, 제어판에서 버튼을 누를 때 시작하게끔 구조를 나중에 바꿀 예정입니다.
    # 일단은 테스트를 위해 같이 켜둡니다.
    capture_thread.start()
    
    # 창 2개 모두 띄우기
    overlay_ui.show()
    control_panel.show()
    
    # 4. 프로그램 종료 시 안전 종료
    app.aboutToQuit.connect(capture_thread.stop)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()