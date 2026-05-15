import os
import datetime
import queue
from core.ocr_processor import TesseractProcessor
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

class OCRThread(QThread):
    # UI의 실시간 로그창으로 메시지를 보낼 시그널
    log_signal = pyqtSignal(str)
    # OCR 완료 보고 시그널 (세션 ID 반환)
    frame_processed = pyqtSignal(int)

    def __init__(self, image_queue):
        super().__init__()
        self.image_queue = image_queue
        self.is_running = True
        self.processor = TesseractProcessor()
        
        self.save_folder = os.getcwd() 
        self.session_files = {} # {session_id: "파일전체경로"}

    @pyqtSlot(str)
    def set_save_folder(self, folder_path):
        self.save_folder = folder_path
    
    @pyqtSlot(int)
    def on_session_started(self, session_id):
        """💡 새로운 스캔이 시작될 때 시각을 기반으로 파일명 결정"""
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scan_{now}.txt"
        full_path = os.path.join(self.save_folder, filename)
        
        self.session_files[session_id] = full_path
        self.log_signal.emit(f"📂 새 세션 시작: {filename}")
        
    def run(self):
        while self.is_running:
            try:
                # 1. 큐에서 캡처된 이미지 데이터 꺼내기 (1초 대기)
                session_id, frame_data = self.image_queue.get(timeout=1)
                extracted_text = self.processor.extract_text(frame_data, lang='kor+eng') # 여기가 본격적인 인식 처리 부분
                
                self.frame_processed.emit(session_id)  # OCR 완료 신호 발송
                
                if extracted_text:
                    self.log_signal.emit(f"📝 {extracted_text}")    # 로그 찍기
                    target_file = self.session_files.get(session_id)
                    
                    try:
                        # [시도 1] 제어판에서 설정한 경로(또는 기본 경로)에 저장 시도
                        with open(target_file, "a", encoding="utf-8") as f:
                            f.write(extracted_text + "\n")
                            
                    except Exception as primary_error:
                        # [에러 발생!] 경로가 잘못되었거나 권한이 없는 경우
                        self.log_signal.emit(f"⚠️ [경고] 설정된 경로({target_file})에 저장 실패: {primary_error}")
                        self.log_signal.emit(f"🔄 {self.fallback_path}에 저장을 시도합니다.")
                        
                        try:
                            # [시도 2] 안전망(Fallback) 경로에 강제 저장
                            with open(self.fallback_path, "a", encoding="utf-8") as f:
                                f.write(extracted_text + "\n")
                                
                        except Exception as fatal_error:
                            # [치명적 에러] 현재 폴더에도 저장을 못 하는 최악의 상황
                            self.log_signal.emit(f"❌ [치명적 오류] 저장에 실패했습니다: {fatal_error}")

            except queue.Empty:
                # 큐가 비어있으면 조용히 다시 대기
                continue

    def stop(self):
        self.is_running = False
        self.wait()