import os
import time
import mss
import mss.tools
from PyQt5.QtCore import QThread, pyqtSlot

class CaptureThread(QThread):
    def __init__(self, fps=5, output_dir="scanline_captures"):
        super().__init__()
        self.fps = fps
        self.output_dir = output_dir
        self.is_running = True
        self.region = {"top": 0, "left": 0, "width": 100, "height": 100}
        os.makedirs(self.output_dir, exist_ok=True)

    @pyqtSlot(int, int, int, int)
    def update_region(self, x, y, width, height):
        """UI의 Signal을 받아 좌표를 갱신하는 Slot"""
        self.region = {"top": y, "left": x, "width": width, "height": height}

    def run(self):
        interval = 1.0 / self.fps
        frame_count = 0

        with mss.mss() as sct:
            while self.is_running:
                loop_start = time.time()
                frame_count += 1

                filename = os.path.join(self.output_dir, f"frame_{frame_count:03d}.png")
                sct_img = sct.grab(self.region)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)

                time_to_wait = interval - (time.time() - loop_start)
                if time_to_wait > 0:
                    time.sleep(time_to_wait)

    def stop(self):
        self.is_running = False
        self.wait()