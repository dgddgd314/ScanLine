import difflib

class TextStitcher:
    """이전 텍스트와 현재 텍스트를 비교하여 중복을 제거하고 새로운 부분만 반환하는 엔진"""
    
    def __init__(self, match_threshold=2):
        self.last_text = ""
        self.match_threshold = match_threshold # 최소 몇 글자가 겹쳐야 중복으로 인정할 것인가

    def reset(self):
        """새로운 스캔 세션이 시작될 때 이전 텍스트 기록을 초기화"""
        self.last_text = ""

    def stitch(self, new_text: str) -> str:
        # 1. 빈 텍스트면 무시
        if not new_text or not new_text.strip():
            return ""

        # 2. 첫 번째 캡처거나, 이전 텍스트가 아예 없을 때 -> 그대로 통과
        if not self.last_text:
            self.last_text = new_text
            return new_text

        # 3. 이전 프레임과 글자가 토시 하나 안 틀리고 똑같을 때 (100% 중복 프레임) -> 스킵
        if self.last_text == new_text:
            return ""

        # 4. difflib을 활용한 패턴 매칭 (가장 길게 겹치는 구간 찾기)
        matcher = difflib.SequenceMatcher(None, self.last_text, new_text)
        match = matcher.find_longest_match(0, len(self.last_text), 0, len(new_text))

        # 5. 매칭된 길이가 임계값(Threshold) 이상이면 겹친다고 판단
        if match.size >= self.match_threshold:
            # 겹치는 부분 '이후'의 텍스트(새로 스크롤되어 올라온 글자)만 잘라냄
            new_part = new_text[match.b + match.size:]
            
            # 다음 비교를 위해 last_text를 현재 텍스트로 업데이트
            self.last_text = new_text 
            
            return new_part.strip()
        else:
            # 겹치는 부분이 아예 없으면 스크롤을 훅 넘긴 것으로 간주하고 줄바꿈 처리
            self.last_text = new_text
            return "\n" + new_text.strip()