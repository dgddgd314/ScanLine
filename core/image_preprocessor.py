import cv2
import numpy as np

class ImagePreprocessor:
    """OCR 인식률을 높이기 위한 이미지 전처리 엔진"""
    
    def process(self, image_np):
        # 1. Grayscale 변환 (mss는 기본적으로 BGRA 포맷으로 이미지를 캡처함)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGRA2GRAY)

        # 2. 이미지 크기 2배 확대 (작은 글씨 인식률 향상)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 3. 이진화 (Otsu's Thresholding: 최적의 임계값을 자동으로 찾아 흑백으로 나눔)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. 여백(Padding) 추가 🌟 가장자리 노이즈 방지용
        # 사방에 30픽셀 두께의 하얀색(255) 테두리를 둘러줍니다.
        padded = cv2.copyMakeBorder(
            binary, 
            top=30, bottom=30, left=30, right=30, 
            borderType=cv2.BORDER_CONSTANT, 
            value=[255, 255, 255]
        )

        return padded