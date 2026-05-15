import time
import queue
from PyQt5.QtCore import QThread, pyqtSignal

class OCRThread(QThread):
    # UI의 실시간 로그창으로 메시지를 보낼 시그널
    log_signal = pyqtSignal(str)

    def __init__(self, image_queue):
        super().__init__()
        self.image_queue = image_queue
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                # 1. 큐에서 캡처된 이미지 데이터 꺼내기 (1초 대기)
                frame_data = self.image_queue.get(timeout=1)
                
                # 2. 검증용 데이터 추출
                shape = frame_data.shape # 예: (100, 800, 4) -> 높이, 너비, 채널(BGRA)
                q_size = self.image_queue.qsize()

                # 3. 제어판 로그로 검증 메시지 전송
                self.log_signal.emit(f"📥 [메모리 수신] 이미지 크기: {shape} | 큐 대기열: {q_size}장")

                # TODO: 실제 OCR이 0.2초 정도 걸린다고 가정하고 딜레이를 줌
                time.sleep(0.2) 

            except queue.Empty:
                # 큐가 비어있으면 조용히 다시 대기
                continue

    def stop(self):
        self.is_running = False
        self.wait()