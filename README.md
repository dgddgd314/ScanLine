# ScanLine (가칭) 텍스트 스크롤 스캐너 🚀

**ScanLine**은 사용자가 화면에 띄워둔 '투명한 가로선' 영역을 통과하는 텍스트를 실시간으로 캡처하고 OCR(광학 문자 인식)하여 자동으로 텍스트 파일에 누적 저장하는 파이썬 기반 백그라운드 유틸리티입니다.

## 💡 프로젝트 개요
뉴스 기사, 긴 웹페이지 등을 스크롤해서 읽을 때, 원하는 텍스트만 손쉽게 추출하기 위해 기획되었습니다. 복잡한 캡처 단축키나 드래그 없이, 직관적인 UI(가로선) 위로 텍스트를 통과시키기만 하면 백그라운드에서 자동으로 글자를 읽어냅니다.

## 🎯 핵심 기능
- **[구현 완료] 플로팅 투명 UI:** 화면 최상단에 항상 고정(Always-on-top)되는 투명 창.
- **[구현 완료] 동적 영역 컨트롤 (Dynamic ROI):** 사용자가 마우스로 선의 가로 길이를 늘이거나, 상하좌우 위치를 자유롭게 조절.
- **[구현 완료] 유령 캡처 (Ghost Mode Capture):** OS 디스플레이 API를 활용하여, UI 창 자체는 사용자에게 보이지만 캡처 결과물에는 텍스트(배경)만 깔끔하게 찍히도록 처리.
- **[구현 완료] 통합 제어판 (Control Panel):** 스캔 제어, 좌표/크기 미세 조정, 투명도 조절, 실시간 로그 확인이 가능한 양방향 동기화 대시보드.
- **[구현 예정] 실시간 연속 캡처 및 OCR:** 지정된 영역을 높은 FPS로 캡처하고 텍스트로 변환.
- **[구현 예정] 스마트 중복 방지 (Stitching):** 스크롤 도중 동일한 문장이 여러 번 인식되더라도 자동으로 문맥을 이어붙여 중복 없는 결과물 생성.

## 🛠️ 기술 스택
- **Language:** Python 3.x
- **Screen Capture:** `mss` (초고속 화면 캡처)
- **UI Framework:** `PyQt5` (투명 프레임리스 오버레이 및 스레드 관리)
- **Image Processing (예정):** `OpenCV` (OCR 인식률 향상을 위한 전처리)
- **OCR Engine (예정):** `Tesseract` 또는 `EasyOCR`

## 📂 프로젝트 구조 (Architecture)
관심사 분리(Separation of Concerns) 원칙에 따라 UI 프론트엔드와 캡처 백그라운드 엔진을 완전히 분리하여 설계되었습니다.

```text
ScanLine/
├── main.py                 # 프로그램 진입점 (UI와 스레드 연결/조립)
├── core/
│   └── capture_engine.py   # 백그라운드 캡처 로직 (QThread)
├── ui/
│   ├── ui_overlay.py       # 사용자 조작용 투명 가로선 창
│   └── control_panel.py    # 설정 및 제어용 통합 대시보드 (신규)
└── .gitignore              # 캐시 및 테스트 이미지 업로드 방지
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

## ⚙️ 제어판 상세 명세 (Dashboard Specification)

| 카테고리 | 주요 기능 | 상세 항목 |
| :--- | :--- | :--- |
| **오버레이 제어** | 초록색 선 속성 | 좌표(X, Y), 선 너비/높이, UI 투명도 슬라이더(0% 지원), 위치 초기화 |
| **스캔 설정** | 캡처 및 OCR | 스캔 시작/정지(Toggle), FPS 조절, OCR 인식 언어(KO/EN) 선택 |
| **데이터 관리** | 저장 및 로그 | TXT 저장 경로 설정, 디버그 모드(이미지 저장 여부), 타임스탬프 기반 작동 로그 |

## 🏗️ 시스템 아키텍처 (Next Architecture: In-Memory Pipeline)
실시간 데이터를 가장 효율적으로 처리하기 위한 인메모리(In-Memory) 큐 기반 데이터 흐름 설계입니다. (Phase 4 구현 예정)

```text
[Screen] 
   ▼ (mss)
[CaptureThread] -> (Pixel Data) -> [In-Memory Queue]
                                         ▼
                                   [OCR Thread] -> (String) -> [TXT File]
                                         ▼
                                   [Live Preview UI]

```

## 🚧 해결해야 할 기술적 과제 & 다음 단계 (Next Steps)

1. **인메모리 릴레이 (In-Memory Relay):** 하드디스크 쓰기(Disk I/O) 과정을 생략하고, RAM 상에서 픽셀 데이터를 직접 큐(Queue)로 전달하여 시스템 병목 현상 최소화.
2. **OCR 엔진 연동 (Tesseract/EasyOCR):** 캡처 스레드(생산자)에서 큐에 넣은 이미지를 꺼내와 텍스트를 추출하는 독립적인 `OCR Thread`(소비자) 파이프라인 구축.
3. **이미지 전처리 (Preprocessing):** 캡처된 이미지를 `OpenCV`를 활용해 흑백화 및 이진화(Binarization) 처리하여 OCR 엔진의 인식 속도와 정확도 극대화.
4. **텍스트 병합 (Deduplication & Stitching):** `difflib` 모듈 등을 활용해 이전 프레임과 현재 프레임의 겹치는 텍스트를 파악하고, 위아래 스크롤 시 발생하는 예외 상황을 고려한 지능형 자동 병합 알고리즘 구현.

## 🏃‍♂️ 실행 방법 (현재 Phase 3 기준)

```bash
# 1. 필수 라이브러리 설치
pip install mss PyQt5

# 2. 프로그램 실행
python main.py