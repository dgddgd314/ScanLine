from PyQt5.QtGui import QColor

class OverlayStyle:
    """오버레이 UI의 테마 색상 정의"""
    
    # 💡 [핵심] 배경 투명도 (0~100% 단위로 여기서 직관적으로 관리)
    BG_OPACITY_PERCENT = 30 
    
    # 내부적으로 QColor에 적용할 실제 알파값(0~255) 자동 계산
    _ALPHA = int((BG_OPACITY_PERCENT / 100) * 255)
    
    # 🟢 대기 상태 (Idle) - 기존 초록색
    IDLE_BG_COLOR = QColor(0, 255, 0, _ALPHA)   # 반투명 배경
    IDLE_LINE_COLOR = QColor(0, 255, 0, 255)    # 중앙 가로선
    IDLE_BORDER_COLOR = QColor(0, 200, 0, 150)  # 테두리 점선

    # 🔴 스캔 중 상태 (Scanning) - 신규 빨간색
    SCAN_BG_COLOR = QColor(255, 0, 0, _ALPHA)
    SCAN_LINE_COLOR = QColor(255, 0, 0, 255)
    SCAN_BORDER_COLOR = QColor(200, 0, 0, 150)