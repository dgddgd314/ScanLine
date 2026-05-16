import pytesseract
from core.ocr.preprocessor.tesseract_preprocessor import TesseractPreprocessor

class TesseractProcessor:
    """Tesseract 엔진을 활용한 텍스트 추출 엔진"""
    
    def __init__(self, tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.preprocessor = TesseractPreprocessor()

    def extract_text(self, raw_image, lang='kor+eng'):
        if raw_image is None:
            return ""

        processed_image = self.preprocessor.process(raw_image)

        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_image, lang=lang, config=custom_config)
        return text.strip()