import os
import time
import mss
import mss.tools
import numpy as np
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal

class CaptureThread(QThread):
    scan_session_started = pyqtSignal(int)  # 새로운 스캔 시작 시 (세션 ID 반환)
    frame_captured = pyqtSignal(int)        # 프레임 하나 캡처 완료 시 (세션 ID 반환)
    
    def __init__(self, image_queue, fps=5, output_dir="scanline_captures"):
        super().__init__()
        self.image_queue = image_queue
        self.fps = fps
        self.output_dir = output_dir
        self.is_running = True
        self.is_capturing = False
        self.debug_mode = False     # 이미지 파일 저장 여부
        self.current_session_id = 0
        self.region = {"top": 0, "left": 0, "width": 100, "height": 100}
        os.makedirs(self.output_dir, exist_ok=True)

    @pyqtSlot(int, int, int, int)
    def update_region(self, x, y, width, height):
        """UI의 Signal을 받아 좌표를 갱신하는 Slot"""
        self.region = {"top": y, "left": x, "width": width, "height": height}

    @pyqtSlot(bool)
    def set_capturing(self, state):
        """제어판의 시작/정지 신호를 받아 캡처 상태 변경"""
        self.is_capturing = state
        if state:
            # 스캔을 시작할 때마다 세션 ID 1 증가 및 UI에 알림
            self.current_session_id += 1
            self.scan_session_started.emit(self.current_session_id)
        
    @pyqtSlot(bool)
    def set_debug_mode(self, state):
        """제어판의 체크박스 상태를 받아옴"""
        self.debug_mode = state
        
    def run(self):
        interval = 1.0 / self.fps
        frame_count = 0

        with mss.mss() as sct:
            while self.is_running:
                loop_start = time.time()
                
                if self.is_capturing: 
                    frame_count += 1
                    sct_img = sct.grab(self.region)
                    
                    img_np = np.array(sct_img)
                    self.image_queue.put((self.current_session_id, img_np))
                    self.frame_captured.emit(self.current_session_id)

                    if self.debug_mode:
                        filename = os.path.join(self.output_dir, f"frame_{frame_count:03d}.png")
                        mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
                                          
                time_to_wait = interval - (time.time() - loop_start)
                if time_to_wait > 0:
                    time.sleep(time_to_wait)

    def stop(self):
        self.is_running = False
        self.wait()