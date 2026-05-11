import mss
import mss.tools
import time
import os

def capture_single_frame(sct, region, output_filepath):
    """
    [핵심 기능] 단일 프레임을 캡처하여 지정된 경로에 이미지 파일로 저장합니다.
    
    Args:
        sct (mss.mss): mss 캡처 객체 (매번 생성하지 않고 외부에서 주입받아 성능 최적화)
        region (dict): 캡처할 화면 영역의 좌표와 크기
        output_filepath (str): 저장할 파일의 전체 경로
    """
    sct_img = sct.grab(region)
    mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_filepath)
    return output_filepath


def run_capture_loop(left, top, width, height, fps=5, duration=5, output_dir="scanline_captures"):
    """
    [제어 로직] 지정된 시간(duration) 및 주기(fps)에 맞춰 캡처 루프를 실행합니다.
    
    Args:
        left, top, width, height: 캡처할 기준 좌표 및 크기
        fps: 초당 캡처 프레임 수
        duration: 총 캡처 진행 시간 (초)
        output_dir: 결과물을 저장할 폴더명
    """
    # 1. 초기 설정 (폴더 생성 및 딜레이 계산)
    os.makedirs(output_dir, exist_ok=True)
    interval = 1.0 / fps 
    region = {"top": top, "left": left, "width": width, "height": height}
    
    print(f"🎥 연속 캡처 루프 시작! (해상도: {width}x{height}, {fps} FPS)")
    
    start_time = time.time()
    frame_count = 0
    
    # 2. mss 객체는 루프 바깥에서 단 한 번만 생성 (리소스 낭비 방지)
    with mss.mss() as sct:
        try:
            # 3. 메인 루프 실행
            while time.time() - start_time < duration:
                loop_start = time.time()
                frame_count += 1
                
                # 파일 경로 생성 및 단일 캡처 함수 호출 (기능 위임)
                filename = os.path.join(output_dir, f"frame_{frame_count:03d}.png")
                capture_single_frame(sct, region, filename)
                
                print(f"저장 완료: {filename}")
                
                # 4. FPS 유지를 위한 시간 보정 대기
                time_to_wait = interval - (time.time() - loop_start)
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
                    
        except KeyboardInterrupt:
            print("\n⚠️ 사용자에 의해 캡처 프로세스가 중단되었습니다.")
            
        print("✅ 캡처 프로세스 정상 종료!")


if __name__ == "__main__":
    # 모듈 단독 실행 시 테스트용 코드
    run_capture_loop(left=100, top=200, width=800, height=100, fps=5, duration=5)