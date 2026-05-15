import cv2
import pytesseract
import numpy as np

class TesseractProcessor:
    def __init__(self):
        # 1단계에서 설치한 Tesseract 실행 파일의 절대 경로를 지정합니다.
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # psm 6: 이미지를 하나의 텍스트 블록으로 가정하고 인식 (스크롤 스캔에 적합)
        self.custom_config = r'--oem 3 --psm 6'

    def extract_text(self, img_np: np.ndarray, lang: str = 'kor+eng') -> str:
        """NumPy 배열(이미지)을 받아 Tesseract를 통해 텍스트로 변환"""
        if img_np is None or img_np.size == 0:
            return ""

        try:
            # mss는 기본적으로 BGRA(알파 채널 포함) 포맷을 반환하므로 BGR로 변환
            if img_np.shape[2] == 4:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
            else:
                img_bgr = img_np
                
            # 가벼운 이미지 전처리: 흑백화(Grayscale) 처리를 통해 인식률 향상
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # 실제 OCR 처리
            text = pytesseract.image_to_string(gray, lang=lang, config=self.custom_config)
            
            # 양쪽 공백 및 줄바꿈 제거 후 반환
            return text.strip()
            
        except Exception as e:
            return f"[OCR 처리 에러]: {e}"