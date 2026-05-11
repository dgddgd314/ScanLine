import mss
import mss.tools

def capture_target_line(left, top, width, height, output_filename="capture_test.png"):
    """
    지정된 좌표와 크기만큼 화면을 캡처하여 파일로 저장합니다.
    """
    with mss.mss() as sct:
        # 캡처할 영역 지정 (우리가 만들 가로선의 위치와 두께라고 상상해 보세요)
        region = {"top": top, "left": left, "width": width, "height": height}
        
        print(f"지정된 영역 캡처 중... (위치: {left},{top} / 크기: {width}x{height})")
        
        # 실제 캡처 수행
        sct_img = sct.grab(region)
        
        # 눈으로 확인하기 위해 이미지 파일로 저장
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_filename)
        print(f"[{output_filename}] 저장 완료!")

if __name__ == "__main__":
    # 테스트: 모니터 좌상단 기준 (x:100, y:200) 위치에서 가로 800px, 세로 60px(글자가 들어갈 만한 두께) 캡처
    capture_target_line(left=100, top=200, width=800, height=60)