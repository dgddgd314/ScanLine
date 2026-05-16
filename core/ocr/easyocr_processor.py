import easyocr
from core.preprocessor.easyocr_preprocessor import EasyOCRPreprocessor
class EasyOCRProcessor:
    """EasyOCR(딥러닝) 엔진을 활용한 텍스트 추출 엔진"""
    
    def __init__(self, langs=['ko', 'en']):
        # 처음 실행 시 AI 모델을 다운로드합니다.
        self.reader = easyocr.Reader(langs, gpu=False)
        self.preprocessor = EasyOCRPreprocessor()

    def extract_text(self, raw_image, lang=None):
        if raw_image is None:
            return ""

        # 전처리
        processed_image = self.preprocessor.process(raw_image)
        
        results = self.reader.readtext(processed_image, detail=0)
        text = " ".join(results)
        return text.strip()