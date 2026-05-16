import cv2
import numpy as np

class TesseractPreprocessor:
    """Tesseract 엔진에 최적화된 이진화 기반 이미지 전처리 엔진"""
    
    def process(self, image_np):
        # 1. 이미 흑백인지 컬러인지 판별)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGRA2GRAY)

        # 2. 이미지 크기 2배 확대 (작은 글씨 인식률 향상)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 3. 이진화 (Tesseract는 칼같은 흑백 이진화 필수)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. 경계선에 걸친 글자 덩어리 지우기
        cleared_binary = self._clear_borders(binary)
        
        # 5. 여백(Padding) 추가
        padded = cv2.copyMakeBorder(
            cleared_binary, 
            top=20, bottom=20, left=20, right=20, 
            borderType=cv2.BORDER_CONSTANT, 
            value=[255, 255, 255]
        )

        return padded
    
    def _clear_borders(self, binary_img):
        """이미지 상하단 경계에 닿아있는 검은색 픽셀 덩어리를 하얗게 지웁니다."""
        height, width = binary_img.shape

        inverted = cv2.bitwise_not(binary_img)
        contours, _ = cv2.findContours(inverted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        top_erase_y = 0
        bottom_erase_y = height
        
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            if y <= 2:
                top_erase_y = max(top_erase_y, y + h)
            
            if (y + h) >= (height - 2):
                bottom_erase_y = min(bottom_erase_y, y)

        result = binary_img.copy()
        
        if top_erase_y > 0:
            cv2.rectangle(result, (0, 0), (width, top_erase_y + 2), 255, -1)

        if bottom_erase_y < height:
            cv2.rectangle(result, (0, bottom_erase_y - 2), (width, height), 255, -1)
        
        return result