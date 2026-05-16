import pytesseract

class TesseractProcessor:
    """Tesseract 엔진을 활용한 텍스트 추출 엔진"""
    
    def __init__(self, tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        # 윈도우 환경 등에서 tesseract.exe 경로를 수동으로 지정해야 할 경우 사용
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, processed_image, lang='kor+eng'):
        """이미 '전처리가 완료된' 이미지 배열을 받아 텍스트만 추출"""
        
        # Tesseract 설정 (PSM 6: 단일 텍스트 블록으로 가정하고 읽기)
        custom_config = r'--oem 3 --psm 6'

        # 텍스트 추출
        text = pytesseract.image_to_string(processed_image, lang=lang, config=custom_config)

        # 양끝 공백 및 불필요한 줄바꿈 제거 후 반환
        return text.strip()