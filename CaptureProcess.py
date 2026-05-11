import mss
import mss.tools
import time
import os

def capture_process(left, top, width, height, fps=5, duration=5):
    """
    지정된 좌표와 크기만큼 화면을 캡처하여 파일로 저장합니다.
    """
    output_dir = "scanline_captures"
    os.makedirs(output_dir, exist_ok=True)
    
    interval = 1.0 / fps
    
    with mss.mss() as sct:
        # 누락 방지를 위해 height(버퍼 존)를 충분히 확보한 영역 설정
        region = {"top": top, "left": left, "width": width, "height": height}
        
        print(f"🎥 연속 캡처 시작! (해상도: {width}x{height}, {fps} FPS)")
        
        start_time = time.time()
        frame_count = 0
        
        try:
            # 설정한 duration(초) 동안 루프를 돕니다.
            while time.time() - start_time < duration:
                loop_start = time.time()
                frame_count += 1
                
                # 파일명에 001, 002 처럼 순차적인 번호 부여
                filename = os.path.join(output_dir, f"frame_{frame_count:03d}.png")
                
                # 캡처 및 파일 저장
                sct_img = sct.grab(region)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
                
                print(f"저장 완료: {filename}")
                
                # 다음 프레임까지 남은 시간 계산 및 대기 (처리 속도 보정)
                time_to_wait = interval - (time.time() - loop_start)
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                    
        except KeyboardInterrupt:
            # 사용자가 강제로 종료(Ctrl+C)했을 때의 안전 장치
            print("\n⚠️ 사용자에 의해 캡처 프로세스가 중단되었습니다.")
            
        print("✅ 캡처 프로세스 정상 종료!")

if __name__ == "__main__":
    # 테스트 설정: 
    # height를 100px로 넉넉하게 잡아 글자 누락을 방지합니다.
    # 1초에 5번(fps=5)씩, 총 5초 동안 캡처를 진행합니다.
    start_capture_process(left=100, top=200, width=800, height=100, fps=5, duration=5)