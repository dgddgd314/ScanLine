# ScanLine (가칭) 텍스트 스크롤 스캐너 🚀

**ScanLine**은 사용자가 화면에 띄워둔 '투명한 가로선' 영역을 통과하는 텍스트를 실시간으로 캡처하고 OCR(광학 문자 인식)하여 자동으로 텍스트 파일에 누적 저장하는 파이썬 기반 백그라운드 유틸리티입니다.

## 💡 프로젝트 개요
뉴스 기사, 긴 웹페이지 등을 스크롤해서 읽을 때, 원하는 텍스트만 손쉽게 추출하기 위해 기획되었습니다. 복잡한 캡처 단축키나 드래그 없이, 직관적인 UI(가로선) 위로 텍스트를 통과시키기만 하면 백그라운드에서 자동으로 글자를 읽어냅니다.

## 🎯 핵심 기능
- **[구현 완료] 플로팅 투명 UI:** 화면 최상단에 항상 고정(Always-on-top)되는 투명 창. 스캔 상태에 따라 색상이 동적으로 변화(초록/빨강)하여 시각적 피드백 제공.
- **[구현 완료] 동적 영역 컨트롤 (Dynamic ROI):** 사용자가 마우스로 선의 가로 길이를 늘이거나, 상하좌우 위치를 자유롭게 조절.
- **[구현 완료] 유령 캡처 (Ghost Mode Capture):** OS 디스플레이 API를 활용하여, UI 창 자체는 사용자에게 보이지만 캡처 결과물에는 텍스트(배경)만 깔끔하게 찍히도록 처리.
- **[구현 완료] 통합 제어판 (Control Panel):** 스캔 제어, 좌표/크기 미세 조정, 실시간 로그 및 OCR 진척도 확인이 가능한 양방향 동기화 대시보드.
- **[구현 완료] 실시간 캡처 및 세션별 자동 저장:** 스캔을 시작할 때마다 자동으로 타임스탬프 기반 텍스트 파일을 생성하고, 높은 FPS로 캡처된 이미지를 큐 기반 파이프라인을 통해 누적 저장.
- **[구현 완료] 하이브리드 OCR 엔진 아키텍처:** 고정밀 딥러닝 기반의 **EasyOCR**과 이진화 기반의 **Tesseract**를 독립된 전처리기 부품과 함께 유연하게 갈아 끼울 수 있는 단일 인터페이스 구조 확립.
- **[고도화 중] 스마트 중복 방지 (Stitching):** 스크롤 도중 동일한 문장이 여러 번 인식되더라도 자동으로 문맥을 이어붙여 중복 없는 결과물을 생성하는 매칭 엔진 고도화 (EasyOCR 특유의 다중 바운딩 박스 분할 인식 대응 튜닝 진행 중).

## 🛠️ 기술 스택
- **Language:** Python 3.x
- **Screen Capture:** `mss` (초고속 화면 캡처)
- **UI Framework:** `PyQt5` (투명 프레임리스 오버레이 및 멀티스레드 제어)
- **Image Processing:** `OpenCV`, `NumPy` (이미지 배열 처리 및 엔진별 전처리)
- **Deep Learning OCR Engine:** `PyTorch`, `EasyOCR` (메인 엔진: 고정밀 영/한 딥러닝 판독)
- **Legacy OCR Engine:** `Tesseract` (`pytesseract`)

## 📂 프로젝트 구조 (Architecture)
관심사 분리(Separation of Concerns) 원칙에 따라 UI 프론트엔드와 캡처 백그라운드 엔진을 완전히 분리하여 설계되었습니다.

```text
ScanLine/
├── main.py                 # 프로그램 진입점 (UI-스레드 조립, PyQt 윈도우 1114 DLL 버그 우회 임포트 적용)
├── core/
│   ├── ocr/                # OCR 비즈니스 로직 패키지
│   │   ├── preprocessor/   # OCR 엔진별 전담 전처리 디렉토리
│   │   │   ├── easyocr_preprocessor.py    # EasyOCR 최적화 전처리 (그레이스케일, 2배율 확대, 이진화 배제)
│   │   │   └── tesseract_preprocessor.py  # Tesseract 최적화 전처리 (칼같은 Otsu 이진화)
│   │   ├── __init__.py
│   │   ├── easyocr_processor.py           # EasyOCR 구동 및 전처리기 내장 캡슐화 클래스
│   │   └── tesseract_processor.py         # Tesseract 구동 및 전처리기 내장 캡슐화 클래스
│   ├── capture_engine.py   # 백그라운드 캡처 로직 (QThread)
│   ├── ocr_engine.py       # 인메모리 큐 데이터 소비 및 실시간 영속성(저장) 제어 스레드
│   └── text_stitcher.py    # 실시간 중복 텍스트 컨텍스트 매칭 및 병합 엔진
├── ui/
│   ├── ui_overlay.py       # 사용자 조작용 투명 가로선 오버레이 UI
│   ├── control_panel.py    # 설정 및 제어용 통합 대시보드 UI
│   └── style_config.py     # UI 디자인 속성 및 테마(색상, 투명도) 중앙 관리 설정 파일
├── scanline_captures/      # [디버그 모드] 캡처된 원본 이미지 저장 디렉토리
└── .gitignore              # 캐시(__pycache__), 디버그 이미지 및 가상환경 환경 설정 제외
```

## 🚀 현재 진행 상황

### Phase 1: 연속 캡처 엔진 구축 (완료)
- `mss` 라이브러리를 활용하여 지정된 좌표와 영역(ROI)을 연속으로 캡처하는 기본 로직 구현.
- **터널링(Tunneling) 방지:** 빠른 스크롤 시 글자 누락을 방지하기 위해 충분한 높이의 **버퍼 존(Buffer Zone)** 확보.

### Phase 2: UI 오버레이 및 스레드 분리 (완료)
- `PyQt5`를 이용한 테두리 없는(Frameless) 투명 조작창 구현 (마우스 드래그 이동/길이 조절 로직 자체 구현).
- **Signal & Slot 패턴 도입:** 메인 UI 스레드와 `CaptureThread`를 분리하여 UI 멈춤(Freezing) 현상 완벽 해결.
- **Windows API 연동 (`SetWindowDisplayAffinity`):** 캡처 시 초록색 UI 그래픽이 글자를 가리는 노이즈 문제를 해결하기 위해, 해당 창을 캡처 대상에서 완전히 제외시킴.

### Phase 3: 통합 제어판(Control Panel) 구축 (완료)
단순 이미지 저장을 넘어, 실시간 데이터를 효율적으로 처리하기 위한 대시보드와 양방향 데이터 동기화를 완벽하게 구현했습니다.

1. **PyQt5 대시보드 구현:** 투명도 조절, 좌표(X/Y/W/H) 수동 입력, FPS 설정, 저장 경로 지정 등 프로그램의 모든 설정을 관리하는 `control_panel.py` 구현.
2. **양방향 데이터 동기화 (Two-way Binding):** 오버레이 창을 마우스로 움직이면 제어판의 숫자가 바뀌고, 제어판 숫자를 바꾸면 창이 움직이도록 Signal & Slot 연동 완료.
3. **스레드 제어 및 타임스탬프 로그:** 캡처 스레드의 대기(Idle)/실행(Running) 상태를 제어판의 시작/정지 스위치로 조작하며, 실시간 작동 시간(Timestamp)이 찍히는 로그(Live Preview) 기능 추가.

### Phase 4: 인메모리 파이프라인(In-Memory Pipeline) 구축 (완료)
디스크 I/O로 인한 병목 현상을 제거하고 `Queue`를 활용한 메모리 기반의 데이터 릴레이를 구현했습니다.

1. **인메모리 릴레이:** 캡처된 화면을 하드디스크에 저장하지 않고, `NumPy` 배열 형태로 RAM의 큐(Queue)에 즉시 전달.
2. **더미 소비자 패턴:** 큐에 쌓인 데이터를 비동기적으로 가져오는 `OCRThread`를 생성하여 데이터의 흐름과 형태를 실시간 모니터링 (디스크 쓰기 완전 제거).
3. **디버그 모드(Debug Mode):** 원할 때만 원본 이미지를 하드디스크에 저장할 수 있도록 토글 기능을 구현하여 테스트의 유연성을 확보.

### Phase 5: 실제 OCR 엔진 연동 및 데이터 영속성 확보 (완료)
더미 스레드에 실제 `Tesseract OCR` 엔진을 연동하여 텍스트 추출 및 파일 저장 파이프라인을 완성했습니다.

1. **비즈니스 로직 분리:** OCR 처리만을 전담하는 `ocr_processor.py`를 독립시켜 확장성(EasyOCR 등 다른 엔진으로의 교체) 확보.
2. **실시간 텍스트 추출:** 큐에서 꺼낸 NumPy 이미지 배열을 OpenCV로 변환 후 텍스트로 추출하여 제어판 로그 UI에 실시간 출력.
3. **Fail-Safe 파일 저장 로직:** 추출된 텍스트를 지정된 `.txt` 파일에 누적(Append) 저장하며, 제어판에서 설정한 경로에 접근이 불가능할 경우 프로그램 다운을 방지하고 현재 폴더의 `output.txt`로 우회 저장하는 안전망 구축.

### Phase 6: UX/UI 고도화 및 세션 기반 데이터 관리 (완료)
생산자-소비자 패턴에서 발생하는 OCR 처리 병목(Bottleneck) 현상을 해결하기 위해 상태 모니터링 시스템을 구축하고 저장 로직을 고도화했습니다.

1. **디자인 속성 분리 및 시각적 피드백:** 투명도 및 색상 정보를 `style_config.py`로 분리하여 유지보수성을 높였으며, 스캔 토글 시 오버레이 UI 색상이 즉각 변화(대기: 초록 / 스캔: 빨강)하도록 구현.
2. **세션별 진행률 모니터링 (Progress Bar):** 캡처 스레드와 OCR 스레드 간에 `Session ID` 꼬리표를 주고받는 시스템을 구축하여, 제어판에서 회차별 전체 프레임 대비 OCR 완료율을 실시간 프로그레스 바로 확인 가능.
3. **타임스탬프 기반 폴더 저장:** 단일 텍스트 파일 덮어쓰기 방식에서 벗어나, 지정한 폴더에 스캔 시작 시각(`scan_YYYYMMDD_HHMMSS.txt`)을 기준으로 매번 독립된 파일을 자동 생성하도록 데이터 관리 구조 개편.
4. **안전 종료 방패 (Fail-Safe Exit):** 앱 종료 시 메모리 큐에 텍스트로 변환되지 못한 미처리 프레임이 남아있을 경우 경고 팝업을 띄워 데이터 유실을 방지.

### Phase 7: 딥러닝 기반 EasyOCR 도입 및 환경 최적화 (완료)
기존 Tesseract 엔진의 영/한 및 기술 용어 오인식 한계를 극복하기 위해 PyTorch 기반의 EasyOCR로 엔진을 대전환하고, 최신 라이브러리 간의 호환성 및 OS 버그를 완벽히 해결했습니다.

1. **임포트 순서 최적화를 통한 DLL 충돌 우회:** 최신 PyTorch가 윈도우 환경에서 PyQt5보다 늦게 임포트될 때 발생하는 악명 높은 `[WinError 1114] (c10.dll)` 에러를 해결하기 위해, `main.py` 최상단에 `import torch`를 강제 배치하여 그래픽 자원 충돌 우회.
2. **의존성 지옥(Dependency Hell) 탈출을 위한 가상환경 격리:** PC 내 글로벌 환경에 설치된 기존 TensorFlow, Qiskit 등의 레거시 라이브러리와 최신 PyTorch/NumPy 2.x 간의 버전 충돌을 원천 차단하기 위해, 프로젝트 내부에 독립된 가상환경(`.venv`) 파이프라인을 구축하여 의존성 완벽 격리.
3. **고정밀 딥러닝 기반 텍스트 판독 성능 확보:** 영문 코드 및 개발 특수 용어가 가짜 숫자로 깨져서 출력되던 Tesseract의 근본적인 한계를 탈출하여, 형태소 판별력이 높은 EasyOCR 딥러닝 모델 기반으로 실전 수준의 데이터 판독 신뢰도 확보.

### Phase 8: 하이브리드 아키텍처 개편 및 전처리 캡슐화 (완료)
프로그램이 특정 OCR 엔진에 종속되는 문제를 해결하고 결합도를 낮추기 위해, 객체 지향 및 관심사 분리(SoC) 원칙에 맞춘 대규모 아키텍처 리팩토링을 단행했습니다.

1. **느슨한 결합(Loose Coupling)을 위한 스레드 책임 경감:** 제어 스레드(`ocr_engine.py`)가 이미지 전처리 단계까지 구체적으로 관여하던 레거시 구조를 전면 파괴. 큐에서 나온 날것의 이미지(`raw_image`)를 프로세서에 가공 없이 그대로 토스하도록 워크플로우를 단순화하여 단일 책임 원칙 준수.
2. **엔진별 전처리 모듈 독립 및 내장화(Encapsulation):** 칼같은 흑백 이진화가 필요한 Tesseract용 전처리기와, 부드러운 그라데이션 윤곽선 보존이 필요한 EasyOCR용 전처리기를 `core/preprocessor/` 하위로 완전히 분리. 각 프로세서 클래스(`Processor`)가 내부 부품으로 전처리기를 스스로 품고 동작하도록 캡슐화 완성.
3. **방어적 프로그래밍(Defensive Programming) 기반 예외 처리:** 상위 레이어의 급격한 구조적 변화나 이미지 입력 채널수(1채널 그레이스케일, 3채널 BGR, 4채널 BGRA 등)의 변동에 상관없이, 전처리 엔진 레이어에서 유연하게 채널을 판별하고 동작하도록 채널 체크 예외 방어막 구축.


## ⚙️ 제어판 상세 명세 (Dashboard Specification)

| 카테고리 | 주요 기능 | 상세 항목 |
| :--- | :--- | :--- |
| **오버레이 제어** | 초록색 선 속성 | 좌표(X, Y), 선 너비/높이, 위치 초기화 |
| **스캔 설정** | 캡처 및 OCR | 스캔 시작/정지(Toggle), FPS 조절, OCR 인식 언어(KO/EN) 선택 |
| **데이터 관리** | 저장 및 로그 | 저장 폴더 지정(타임스탬프 자동 생성), 디버그 모드(이미지 저장 여부) |
| **진행 상태** | 모니터링 | 글로벌 총 캡처/처리 카운터, 세션별 실시간 프로그레스 바, 실시간 텍스트 로그 |

## 🏗️ 시스템 아키텍처 (In-Memory Pipeline)
실시간 데이터를 가장 효율적으로 처리하기 위한 인메모리(In-Memory) 큐 기반 데이터 흐름 설계입니다.

```text
[Screen] 
   ▼ (mss)
[CaptureThread] ➔ (Pixel Data: BGRA Numpy) ➔ [In-Memory Queue]
                                                    ▼
                                            [OCR Thread (Workflow)]
                                                    ▼ (Pass Raw Image)
                                            [EasyOCR / Tesseract Processor]
                                                    ▼ (Internal Preprocessing)
                                            [Engine-Specific Preprocessor]
                                                    ▼ (Extract Text)
                                            [TextStitcher (Context Stitching)]
                                                    ▼
                                            [TXT File & Live Preview UI]
```

## 🚧 해결해야 할 기술적 과제 & 다음 단계 (Next Steps)

1. **EasyOCR 문장 중복 방지 및 TextStitcher 알고리즘 최적화:** EasyOCR 엔진 특성상 하나의 문장을 여러 개의 바운딩 박스로 쪼개어 인식하여 중복 데이터가 쌓이는 현상이 발생함. 이를 해결하기 위해 `readtext(paragraph=True)` 옵션을 테스트하고, `TextStitcher`의 시퀀스 매칭 임계값(Threshold)을 정밀 조율하여 스크롤 누적 버그 완벽 해결.
2. **엔진별 맞춤형 전처리 파이프라인 고도화:** 아키텍처 분리는 완료되었으므로, 스크롤 속도 변화에 따라 상하단 경계면에 생기는 글자 잔상 노이즈를 더 완벽히 차단할 수 있도록 `_clear_borders` 지움 마진(Margin) 알고리즘 고도화 및 EasyOCR 내부 대비(Contrast) 옵션 튜닝.

## 🏃‍♂️ 실행 방법 (가상환경 격리 권장)

윈도우 환경에서 타 라이브러리(TensorFlow, Qiskit 등)와의 NumPy 버전 충돌을 방지하고, PyQt5와 PyTorch 간의 1114 DLL 로드 버그를 피하기 위해 가상환경 환경 구축 및 임포트 순서 최적화가 완료되었습니다. tesseract 엔진으로 구동하기 위해서는 운영체제에 [Tesseract-OCR](https://github.com/UB-Mannheim/tesseract/wiki) (한국어 팩 포함)이 설치되어 있어야 합니다.

```bash
# 1. 프로젝트 폴더 내 독립 가상환경 생성 및 활성화
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1

# 2. 필수 라이브러리 및 최신 AI 패키지 설치
pip install torch torchvision torchaudio easyocr PyQt5 opencv-python mss pytesseract

# 3. 프로그램 실행 (main.py 내 최상단 임포트 규칙 자동 적용)
python main.py