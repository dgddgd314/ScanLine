import cv2
import numpy as np

class EasyOCRPreprocessor:
    """EasyOCR 딥러닝 엔진에 최적화된 가볍고 부드러운 이미지 전처리 엔진"""
    
    def process(self, image_np):
        # 1. Grayscale 변환 (컬러 노이즈 제거)
        gray = cv2.cvtColor(image_np, cv2.COLOR_BGRA2GRAY)

        # 2. 이미지 크기 2배 확대 (딥러닝 엔진이 글자 윤곽을 더 잘 잡도록 보간법 적용)
        # ★ 핵심: 이진화(cv2.threshold)를 완전히 빼서 글꼴의 안티앨리어싱(부드러운 곡선)을 보존합니다.
        resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # 3. 경계선에 걸친 불완전한 텍스트 줄(Line) 전체 지우기
        cleared = self._clear_borders(resized)
        
        # 4. 여백(Padding) 추가 (EasyOCR이 외곽 경계면 글자를 놓치지 않게 흰색 테두리 추가)
        padded = cv2.copyMakeBorder(
            cleared, 
            top=20, bottom=20, left=20, right=20, 
            borderType=cv2.BORDER_CONSTANT, 
            value=[255, 255, 255]
        )

        return padded
    
    def _clear_borders(self, gray_img):
        """이미지 상하단 경계에 잘린 글자가 포함된 가로줄 전체를 하얗게 덮어버립니다."""
        height, width = gray_img.shape

        # 윤곽선(Contours)을 찾기 위해 함수 내부에서만 임시 이진화(인버전 포함) 진행
        _, binary = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        top_erase_y = 0
        bottom_erase_y = height

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)

            # 해상도가 2배 커진 상태이므로 경계선 마진을 4픽셀로 부여
            if y <= 4:
                top_erase_y = max(top_erase_y, y + h)
            
            if (y + h) >= (height - 4):
                bottom_erase_y = min(bottom_erase_y, y)

        # 실제 결과물은 부드러운 그레이스케일(원본 복사본) 위에 하얀색 박스를 칩니다.
        result = gray_img.copy()

        if top_erase_y > 0:
            cv2.rectangle(result, (0, 0), (width, top_erase_y + 4), 255, -1)

        if bottom_erase_y < height:
            cv2.rectangle(result, (0, bottom_erase_y - 4), (width, height), 255, -1)

        return result