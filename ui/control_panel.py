import os
import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QGroupBox, QComboBox, QTextEdit, 
                             QCheckBox, QSpinBox, QFileDialog, QProgressBar, 
                             QScrollArea, QMessageBox, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

class ControlPanel(QWidget):
    scan_toggled = pyqtSignal(bool)
    reset_requested = pyqtSignal()
    debug_mode_changed = pyqtSignal(bool)
    fps_changed = pyqtSignal(int)
    geometry_changed = pyqtSignal(int, int, int, int) # x, y, w, h
    save_path_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_scanning = False
        self.total_captured = 0
        self.total_processed = 0
        self.session_total_frames = {}      # {세션ID: 찍힌 총 사진 수}
        self.session_processed_frames = {}  # {세션ID: 처리된 사진 수}
        self.session_progress_bars = {}     # {세션ID: QProgressBar 객체}
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ScanLine Control Panel')
        self.setGeometry(100, 100, 450, 650)
        
        main_layout = QVBoxLayout()

        # ==========================================
        # 1. 오버레이 제어 그룹 (Overlay Controls)
        # ==========================================
        overlay_group = QGroupBox("1. Overlay Controls")
        overlay_layout = QVBoxLayout()

        # 💡 [추가] 좌표 및 크기 스핀박스 (X, Y, W, H)
        geom_layout = QHBoxLayout()
        self.spin_x = QSpinBox(); self.spin_x.setRange(0, 5000); self.spin_x.setPrefix("X: ")
        self.spin_y = QSpinBox(); self.spin_y.setRange(0, 5000); self.spin_y.setPrefix("Y: ")
        self.spin_w = QSpinBox(); self.spin_w.setRange(100, 5000); self.spin_w.setPrefix("W: ")
        self.spin_h = QSpinBox(); self.spin_h.setRange(50, 1000); self.spin_h.setPrefix("H: ")
        
        for spin in [self.spin_x, self.spin_y, self.spin_w, self.spin_h]:
            geom_layout.addWidget(spin)
            spin.valueChanged.connect(self.on_geometry_spin_changed)

        # 초기화 버튼
        self.reset_btn = QPushButton("Reset UI Position")
        self.reset_btn.clicked.connect(self.reset_requested.emit)

        overlay_layout.addLayout(geom_layout)
        overlay_layout.addWidget(self.reset_btn)
        overlay_group.setLayout(overlay_layout)

        # ==========================================
        # 2. 스캔 설정 그룹 (Scan Settings)
        # ==========================================
        scan_group = QGroupBox("2. Scan Settings")
        scan_layout = QVBoxLayout()

        # 💡 [추가] FPS 조절
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel("Capture FPS:"))
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 30)
        self.fps_spin.setValue(5)
        self.fps_spin.valueChanged.connect(self.fps_changed.emit)
        fps_layout.addWidget(self.fps_spin)

        # OCR 언어
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel("OCR Language:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Korean + English", "Korean", "English"])
        lang_layout.addWidget(self.lang_combo)

        # 시작 버튼
        self.toggle_btn = QPushButton("Start Scanning ▶")
        self.toggle_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 15px; font-size: 14px;")
        self.toggle_btn.clicked.connect(self.on_toggle_clicked)

        scan_layout.addLayout(fps_layout)
        scan_layout.addLayout(lang_layout)
        scan_layout.addWidget(self.toggle_btn)
        scan_group.setLayout(scan_layout)

        # ==========================================
        # 3. 데이터 관리 (Data Management)
        # ==========================================
        data_group = QGroupBox("3. Data Management")
        data_layout = QVBoxLayout()

        # 💡 [추가] 저장 경로 설정
        path_layout = QHBoxLayout()
        self.path_label = QLabel(os.path.abspath("output.txt"))
        self.path_label.setStyleSheet("color: gray;")
        self.path_btn = QPushButton("Set TXT Path")
        self.path_btn.clicked.connect(self.select_save_path)
        path_layout.addWidget(self.path_btn)
        path_layout.addWidget(self.path_label, stretch=1)

        # 디버그 모드
        self.debug_check = QCheckBox("Save Original Images (Debug Mode)")
        self.debug_check.stateChanged.connect(self.on_debug_mode_changed)
        
        data_layout.addLayout(path_layout)
        data_layout.addWidget(self.debug_check)
        data_group.setLayout(data_layout)
        
        # 글로벌 카운터
        self.global_counter_label = QLabel("Total Captured: 0장  |  OCR Completed: 0장")
        self.global_counter_label.setStyleSheet("font-weight: bold; color: #333; margin-top: 10px;")
        
        # 세션별 프로그레스 바를 담을 스크롤 영역
        self.progress_scroll = QScrollArea()
        self.progress_scroll.setWidgetResizable(True)
        self.progress_scroll.setFixedHeight(120) # 스크롤 창 높이 고정
        
        self.progress_container = QWidget()
        self.progress_layout = QVBoxLayout(self.progress_container)
        self.progress_layout.setAlignment(Qt.AlignTop)
        self.progress_scroll.setWidget(self.progress_container)
        
        data_layout.addWidget(self.global_counter_label)
        data_layout.addWidget(self.progress_scroll)
        data_group.setLayout(data_layout)

        # ==========================================
        # 4. 미리보기 (Live Preview)
        # ==========================================
        log_group = QGroupBox("Live Preview")
        log_layout = QVBoxLayout()
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console)
        log_group.setLayout(log_layout)

        # 조립
        main_layout.addWidget(overlay_group)
        main_layout.addWidget(scan_group)
        main_layout.addWidget(data_group)
        main_layout.addWidget(log_group)
        
        self.setLayout(main_layout)

    # --- 이벤트 함수 ---
    def on_toggle_clicked(self):
        self.is_scanning = not self.is_scanning
        if self.is_scanning:
            self.toggle_btn.setText("Stop Scanning 🛑")
            self.toggle_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 15px; font-size: 14px;")
        else:
            self.toggle_btn.setText("Start Scanning ▶")
            self.toggle_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 15px; font-size: 14px;")
        self.scan_toggled.emit(self.is_scanning)
        
    def on_debug_mode_changed(self, state):
        self.debug_mode_changed.emit(state == Qt.Checked)

    def select_save_path(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Text File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_name:
            self.path_label.setText(file_name)
            self.save_path_changed.emit(file_name)

    def on_geometry_spin_changed(self):
        x = self.spin_x.value()
        y = self.spin_y.value()
        w = self.spin_w.value()
        h = self.spin_h.value()
        self.geometry_changed.emit(x, y, w, h)

    def update_geometry_spins(self, x, y, w, h):
        """오버레이 창이 마우스로 움직일 때 스핀박스 값 업데이트 (순환 참조 방지용 블록 포함 필요)"""
        self.spin_x.blockSignals(True); self.spin_x.setValue(x); self.spin_x.blockSignals(False)
        self.spin_y.blockSignals(True); self.spin_y.setValue(y); self.spin_y.blockSignals(False)
        self.spin_w.blockSignals(True); self.spin_w.setValue(w); self.spin_w.blockSignals(False)
        self.spin_h.blockSignals(True); self.spin_h.setValue(h); self.spin_h.blockSignals(False)

# --- 진행률 업데이트 로직 ---
    @pyqtSlot(int)
    def on_session_started(self, session_id):
        # 새로운 스캔 시작 시, 새 프로그레스 바 생성
        bar = QProgressBar()
        bar.setValue(0)
        bar.setFormat(f"Scan #{session_id}: %v/%m장 완료 (%p%)")
        bar.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
        
        self.session_progress_bars[session_id] = bar
        self.session_total_frames[session_id] = 0
        self.session_processed_frames[session_id] = 0
        
        # 스크롤 뷰 맨 위에 새 바를 추가 (최신 스캔이 위로 오도록)
        self.progress_layout.insertWidget(0, bar)

    @pyqtSlot(int)
    def on_frame_captured(self, session_id):
        self.total_captured += 1
        self.session_total_frames[session_id] += 1
        self.update_global_counter()
        
        # 바의 최대치(100%)를 찍힌 사진 수로 실시간 업데이트
        bar = self.session_progress_bars[session_id]
        bar.setMaximum(self.session_total_frames[session_id])

    @pyqtSlot(int)
    def on_frame_processed(self, session_id):
        self.total_processed += 1
        self.session_processed_frames[session_id] += 1
        self.update_global_counter()
        
        # 바의 현재 값을 처리된 사진 수로 업데이트
        bar = self.session_progress_bars[session_id]
        bar.setValue(self.session_processed_frames[session_id])

    def update_global_counter(self):
        self.global_counter_label.setText(f"Total Captured: {self.total_captured}장  |  OCR Completed: {self.total_processed}장")

    # --- 안전 종료 ---
    def closeEvent(self, event):
        """사용자가 창의 X 버튼을 눌러 끌 때 발동"""
        if self.total_captured > self.total_processed:
            reply = QMessageBox.warning(
                self, 
                '종료 경고',
                f'아직 OCR 처리가 진행 중인 데이터가 {self.total_captured - self.total_processed}장 남아있습니다!\n강제로 종료하시면 남은 데이터는 저장되지 않습니다.\n\n정말 종료하시겠습니까?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                event.accept()
                QApplication.instance().quit() # 앱 완전 종료
            else:
                event.ignore() # 창 닫기 취소
        else:
            event.accept()
            QApplication.instance().quit()
            
            
    def log_message(self, message):
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_console.append(f"[{current_time}] {message}")