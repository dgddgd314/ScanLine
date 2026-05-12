# ScanLine (가칭) 텍스트 스크롤 스캐너 🚀

**ScanLine**은 사용자가 화면에 띄워둔 '투명한 가로선' 영역을 통과하는 텍스트를 실시간으로 캡처하고 OCR(광학 문자 인식)하여 자동으로 텍스트 파일에 누적 저장하는 파이썬 기반 백그라운드 유틸리티입니다.

## 💡 프로젝트 개요
뉴스 기사, 긴 웹페이지 등을 스크롤해서 읽을 때, 원하는 텍스트만 손쉽게 추출하기 위해 기획되었습니다. 복잡한 캡처 단축키나 드래그 없이, 직관적인 UI(가로선) 위로 텍스트를 통과시키기만 하면 백그라운드에서 자동으로 글자를 읽어냅니다.

## 🎯 핵심 기능 (구현 예정)
- **플로팅 투명 UI:** 화면 최상단에 항상 고정(Always-on-top)되는 투명 창.
- **동적 영역 컨트롤 (Dynamic ROI):** 사용자가 마우스로 선의 가로 길이를 늘이거나, 상하좌우 위치를 자유롭게 조절.
- **실시간 연속 캡처 및 OCR:** 지정된 영역을 높은 FPS로 캡처하고 텍스트로 변환.
- **스마트 중복 방지 (Stitching):** 스크롤 도중 동일한 문장이 여러 번 인식되더라도 자동으로 문맥을 이어붙여(Text Stitching) 중복 없는 깔끔한 결과물 생성.

## 🛠️ 기술 스택
- **Language:** Python 3.x
- **Screen Capture:** `mss` (초고속 화면 캡처)
- **UI Framework (예정):** `PyQt5` 또는 `PySide6`
- **Image Processing (예정):** `OpenCV` (OCR 인식률 향상을 위한 전처리)
- **OCR Engine (예정):** `Tesseract` 또는 `EasyOCR`

## 🚀 현재 진행 상황

### Phase 1: 연속 캡처 엔진 구축 (완료)
- `mss` 라이브러리를 활용하여 지정된 좌표와 영역(ROI)을 연속으로 캡처하는 기본 로직 구현.
- **터널링(Tunneling) 방지:** 빠른 스크롤 시 글자 누락을 방지하기 위해, 시각적인 '선' 대신 충분한 높이(예: 100px)의 **버퍼 존(Buffer Zone)**을 두고 캡처하도록 설계.
- 목표 FPS에 맞춰 프레임별로 `scanline_captures` 폴더에 이미지를 분리 저장하는 테스트 완료.

## 📚 코어 모듈 명세 (API Reference)
현재 `Phase 1`에서 구현된 `capture_engine.py`의 핵심 함수 구조입니다. 단일 책임 원칙(SRP)에 따라 단일 캡처와 반복 제어 로직을 분리하여 구현했습니다.

### 1. `capture_single_frame(sct, region, output_filepath)`
단일 프레임을 캡처하여 지정된 경로에 이미지 파일로 저장하는 순수 함수입니다. 추후 OCR 파이프라인 연결 시 메모리 기반 이미지 처리로 확장이 용이하도록 설계되었습니다.

* **Parameters:**
  * `sct` (`mss.mss`): 리소스 낭비를 막고 캡처 속도를 높이기 위해 외부에서 한 번만 생성하여 주입받는 mss 캡처 객체.
  * `region` (`dict`): 캡처할 화면 영역의 좌표와 크기를 담은 딕셔너리 (예: `{"top": 200, "left": 100, "width": 800, "height": 100}`).
  * `output_filepath` (`str`): 캡처한 이미지를 저장할 전체 파일 경로.
* **Returns:**
  * `str`: 성공적으로 저장된 이미지의 파일 경로(`output_filepath`)를 반환합니다.

### 2. `run_capture_loop(left, top, width, height, fps=5, duration=5, output_dir="scanline_captures")`
지정된 시간(duration) 및 주기(fps)에 맞춰 캡처 루프를 실행하고, 디렉토리 생성 및 FPS 유지를 위한 동적 딜레이(Delay)를 관리하는 제어 함수입니다.

* **Parameters:**
  * `left`, `top` (`int`): 캡처 영역의 좌측 상단 기준 화면 절대 좌표(px).
  * `width`, `height` (`int`): 캡처할 영역의 가로, 세로 크기(px). `height`는 스크롤 터널링 방지를 위해 폰트 크기보다 넉넉하게 설정해야 합니다.
  * `fps` (`int`, optional): 초당 캡처 프레임 수. (기본값: 5)
  * `duration` (`int`, optional): 총 캡처 루프 진행 시간(초). (기본값: 5)
  * `output_dir` (`str`, optional): 결과물 프레임 이미지를 순차적으로 저장할 폴더명. (기본값: `"scanline_captures"`)
* **Returns:**
  * `None`: 루프가 정상적으로 종료되거나 사용자에 의해 중단(KeyboardInterrupt)되면 종료되며 별도의 반환값은 없습니다.

## 🚧 해결해야 할 기술적 과제 & 다음 단계 (Next Steps)

1. **이미지 전처리 (Preprocessing):** 캡처된 이미지를 `OpenCV`로 흑백화/이진화하여 OCR 엔진의 인식률 극대화.
2. **텍스트 병합 (Deduplication & Stitching):** `difflib` 등을 활용해 이전 프레임과 현재 프레임의 겹치는 텍스트를 파악하고, 역방향 스크롤(위로 올리기) 시 발생하는 예외 상황 처리.
3. **아키텍처 리팩토링:** 화면 캡처(빠름)와 OCR 처리(느림) 간의 병목 현상을 해결하기 위해, `threading`과 `queue`를 활용한 **생산자-소비자 패턴(Producer-Consumer Pattern)** 도입.
4. **UI 오버레이 구현:** 투명한 배경을 가진 동적 조절 가능 윈도우 창 구현.

## 🏃‍♂️ 실행 방법 (현재 Phase 1 기준)

```bash
# 필수 라이브러리 설치
pip install mss

# 캡처 모듈 테스트 실행
python capture_engine.py