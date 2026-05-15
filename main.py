import sys
import queue
from PyQt5.QtWidgets import QApplication
from ui.ui_overlay import ScanLineUI
from ui.control_panel import ControlPanel
from core.capture_engine import CaptureThread
from core.ocr_engine import OCRThread

def main():
    app = QApplication(sys.argv)
    
    # 이미지 메모리 버퍼
    image_queue = queue.Queue()
    
    overlay_ui = ScanLineUI()
    control_panel = ControlPanel()
    
    capture_thread = CaptureThread(image_queue=image_queue, fps=5)
    ocr_thread = OCRThread(image_queue=image_queue)

    # [UI <-> UI 연결]
    control_panel.reset_requested.connect(overlay_ui.reset_position)
    control_panel.geometry_changed.connect(overlay_ui.set_geometry_from_panel)
    overlay_ui.region_changed.connect(control_panel.update_geometry_spins)

    # [UI <-> 백그라운드 스레드 연결]
    overlay_ui.region_changed.connect(capture_thread.update_region)
    control_panel.fps_changed.connect(lambda fps: setattr(capture_thread, 'fps', fps))
    
    # 스캔 시작/정지 토글 연결
    control_panel.scan_toggled.connect(capture_thread.set_capturing)
    control_panel.scan_toggled.connect(lambda is_on: control_panel.log_message(f"Scan Mode: {'ON' if is_on else 'OFF'}"))
    control_panel.scan_toggled.connect(overlay_ui.set_scanning_state)
    
    # 디버그 모드 토글 연결
    control_panel.debug_mode_changed.connect(capture_thread.set_debug_mode)
    control_panel.debug_mode_changed.connect(lambda is_on: control_panel.log_message(f"Debug Mode (File Save): {'ON' if is_on else 'OFF'}"))
    
    # 제어판의 텍스트 저장 경로 업데이트 -> OCR 스레드에 경로 동기화
    control_panel.save_folder_changed.connect(ocr_thread.set_save_folder)
    
    # 캡처/OCR 진행률 시그널 -> 제어판 UI 업데이트 연결
    capture_thread.scan_session_started.connect(control_panel.on_session_started)
    capture_thread.scan_session_started.connect(ocr_thread.on_session_started)
    capture_thread.frame_captured.connect(control_panel.on_frame_captured)
    
    ocr_thread.frame_processed.connect(control_panel.on_frame_processed)
    
    # OCR 스레드 로그 출력
    ocr_thread.log_signal.connect(control_panel.log_message)
    
    # 초기 상태 동기화 및 실행
    capture_thread.update_region(
        overlay_ui.x(), overlay_ui.y(), overlay_ui.width(), overlay_ui.height()
    )
    control_panel.update_geometry_spins(overlay_ui.x(), overlay_ui.y(), overlay_ui.width(), overlay_ui.height())
    
    # 처음에 캡처 스레드는 바로 시작하지 않고, 제어판에서 버튼을 누를 때 시작하게
    capture_thread.start()
    ocr_thread.start()
    
    control_panel.log_message("System Initialized. In-Memory Queue Ready.")
    
    # 창 2개 모두 띄우기
    overlay_ui.show()
    control_panel.show()
    
    # 4. 프로그램 종료 시 안전 종료
    app.aboutToQuit.connect(capture_thread.stop)
    app.aboutToQuit.connect(ocr_thread.stop)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()