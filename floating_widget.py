import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QDialog, QLineEdit, QFormLayout, QDoubleSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont
from autoclicker_core import AutoClickerWorker, load_config, save_config
from calibration_overlay import CalibrationOverlay

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações dos 2 Passos & Anti-Ad - AutoClicker PC")
        self.setFixedWidth(440)

        config = load_config()

        layout = QFormLayout(self)

        self.cb_ad = QCheckBox("Ativar Fechamento Automático de Anúncios")
        self.cb_ad.setChecked(config.get("ad_auto_close", True))

        self.et_ad_k = QLineEdit(", ".join(config.get("ad_keywords", [])))

        self.et_k1 = QLineEdit(", ".join(config.get("step1_keywords", [])))
        self.sp_t1 = QDoubleSpinBox()
        self.sp_t1.setRange(1.0, 30.0)
        self.sp_t1.setValue(float(config.get("step1_timeout", 4.0)))

        self.et_k2 = QLineEdit(", ".join(config.get("step2_keywords", [])))
        self.sp_t2 = QDoubleSpinBox()
        self.sp_t2.setRange(1.0, 30.0)
        self.sp_t2.setValue(float(config.get("step2_timeout", 5.0)))

        self.sp_delay = QDoubleSpinBox()
        self.sp_delay.setRange(0.5, 20.0)
        self.sp_delay.setValue(float(config.get("step_delay", 2.0)))

        layout.addRow("--- PROTEÇÃO ANTI-AD ---", QLabel(""))
        layout.addRow(self.cb_ad)
        layout.addRow("Palavras-chave de Anúncios:", self.et_ad_k)

        layout.addRow("--- PASSO 1: Vortex / Notificação ---", QLabel(""))
        layout.addRow("Palavras-chave Passo 1:", self.et_k1)
        layout.addRow("Timeout Passo 1 (s):", self.sp_t1)

        layout.addRow("--- PASSO 2: Navegador / Download ---", QLabel(""))
        layout.addRow("Palavras-chave Passo 2:", self.et_k2)
        layout.addRow("Timeout Passo 2 (s):", self.sp_t2)

        layout.addRow("--- TRANSIÇÃO ---", QLabel(""))
        layout.addRow("Delay entre passos (s):", self.sp_delay)

        btn_save = QPushButton("Salvar Configurações")
        btn_save.setStyleSheet("background-color: #1E88E5; color: white; padding: 8px; font-weight: bold;")
        btn_save.clicked.connect(self.save_and_close)
        layout.addRow(btn_save)

    def save_and_close(self):
        ad_k = [k.strip() for k in self.et_ad_k.text().split(",") if k.strip()]
        k1 = [k.strip() for k in self.et_k1.text().split(",") if k.strip()]
        k2 = [k.strip() for k in self.et_k2.text().split(",") if k.strip()]

        config = load_config()
        config["ad_auto_close"] = self.cb_ad.isChecked()
        config["ad_keywords"] = ad_k
        config["step1_keywords"] = k1
        config["step1_timeout"] = self.sp_t1.value()
        config["step2_keywords"] = k2
        config["step2_timeout"] = self.sp_t2.value()
        config["step_delay"] = self.sp_delay.value()
        save_config(config)
        self.accept()


class FloatingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()

        # Configuração da Janela Flutuante (Sempre no topo, sem bordas)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(320)

        # Worker de Automação
        self.worker = AutoClickerWorker()
        self.worker.status_changed.connect(self.update_status)
        self.worker.log_added.connect(self.add_log)
        self.worker.count_updated.connect(self.update_count)
        self.worker.ad_count_updated.connect(self.update_ad_count)
        self.worker.start()

        self.init_ui()
        self.update_exclude_rect()

    def update_exclude_rect(self):
        geo = self.geometry()
        rect = (geo.left(), geo.top(), geo.right(), geo.bottom())
        self.worker.exclude_rect = rect

    def moveEvent(self, event):
        super().moveEvent(event)
        self.update_exclude_rect()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_exclude_rect()

    def init_ui(self):
        container = QFrame(self)
        container.setStyleSheet(
            "QFrame { "
            "background-color: #E6121824; "
            "border: 1px solid #1E88E5; "
            "border-radius: 16px; "
            "}"
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        content_layout = QVBoxLayout(container)
        content_layout.setContentsMargins(14, 12, 14, 12)

        # Cabeçalho
        header_layout = QHBoxLayout()
        title_label = QLabel("⚡ AutoClicker PC + Anti-Ad")
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white; border: none;")

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(22, 22)
        btn_close.setStyleSheet(
            "QPushButton { color: white; background: transparent; border: none; font-weight: bold; } "
            "QPushButton:hover { color: #FF5252; }"
        )
        btn_close.clicked.connect(self.close_app)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        content_layout.addLayout(header_layout)

        # Divisor
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #33FFFFFF; border: none;")
        divider.setFixedHeight(1)
        content_layout.addWidget(divider)

        # Status Atual
        self.lbl_status = QLabel("Status: Parado")
        self.lbl_status.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.lbl_status.setStyleSheet("color: #00E676; border: none;")
        content_layout.addWidget(self.lbl_status)

        # Contador de Downloads e Ads
        self.lbl_count = QLabel("Downloads concluídos: 0")
        self.lbl_count.setFont(QFont("Segoe UI", 9))
        self.lbl_count.setStyleSheet("color: #E0E0E0; border: none;")
        content_layout.addWidget(self.lbl_count)

        self.lbl_ad_count = QLabel("Anúncios fechados: 0 🛡️")
        self.lbl_ad_count.setFont(QFont("Segoe UI", 8))
        self.lbl_ad_count.setStyleSheet("color: #FFB74D; border: none;")
        content_layout.addWidget(self.lbl_ad_count)

        # Pontos Calibrados P1 e P2
        config = load_config()
        p1 = f"P1 (Vortex): ({config['step1_x']}, {config['step1_y']})"
        p2 = f"P2 (Navegador): ({config['step2_x']}, {config['step2_y']})"
        self.lbl_coords = QLabel(f"{p1}\n{p2}")
        self.lbl_coords.setFont(QFont("Segoe UI", 8))
        self.lbl_coords.setStyleSheet("color: #90A4AE; border: none;")
        content_layout.addWidget(self.lbl_coords)

        # Botões Iniciar e Calibrar
        btn_layout = QHBoxLayout()

        self.btn_toggle = QPushButton("Iniciar")
        self.btn_toggle.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.btn_toggle.setStyleSheet(
            "background-color: #00E676; color: black; border-radius: 6px; padding: 6px; font-weight: bold;"
        )
        self.btn_toggle.clicked.connect(self.toggle_automation)

        self.btn_calibrate = QPushButton("Calibrar 2 Pontos")
        self.btn_calibrate.setFont(QFont("Segoe UI", 9))
        self.btn_calibrate.setStyleSheet(
            "background-color: #37474F; color: white; border-radius: 6px; padding: 6px;"
        )
        self.btn_calibrate.clicked.connect(self.open_calibration)

        btn_layout.addWidget(self.btn_toggle)
        btn_layout.addWidget(self.btn_calibrate)
        content_layout.addLayout(btn_layout)

        # Botões secundários
        btn_layout2 = QHBoxLayout()

        btn_settings = QPushButton("⚙️ Configs")
        btn_settings.setStyleSheet("background-color: #263238; color: white; border-radius: 4px; padding: 4px;")
        btn_settings.clicked.connect(self.open_settings)

        btn_reset = QPushButton("↺ Reset")
        btn_reset.setStyleSheet("background-color: #263238; color: white; border-radius: 4px; padding: 4px;")
        btn_reset.clicked.connect(self.reset_counter)

        btn_layout2.addWidget(btn_settings)
        btn_layout2.addWidget(btn_reset)
        content_layout.addLayout(btn_layout2)

        # Último Log
        self.lbl_log = QLabel("Pronto para automatizar...")
        self.lbl_log.setFont(QFont("Segoe UI", 8))
        self.lbl_log.setStyleSheet("color: #B0BEC5; border: none;")
        self.lbl_log.setWordWrap(True)
        content_layout.addWidget(self.lbl_log)

    def toggle_automation(self):
        new_state = not self.worker.running
        self.worker.set_running(new_state)

        if new_state:
            self.btn_toggle.setText("Pausar")
            self.btn_toggle.setStyleSheet(
                "background-color: #FF9800; color: black; border-radius: 6px; padding: 6px; font-weight: bold;"
            )
        else:
            self.btn_toggle.setText("Iniciar")
            self.btn_toggle.setStyleSheet(
                "background-color: #00E676; color: black; border-radius: 6px; padding: 6px; font-weight: bold;"
            )

    def update_status(self, status):
        self.lbl_status.setText(f"Status: {status}")

    def add_log(self, log_type, message):
        import datetime
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_log.setText(f"[{now_str}] [{log_type}] {message}")

    def update_count(self, count):
        self.lbl_count.setText(f"Downloads concluídos: {count}")

    def update_ad_count(self, ad_count):
        self.lbl_ad_count.setText(f"Anúncios fechados: {ad_count} 🛡️")

    def open_calibration(self):
        self.overlay = CalibrationOverlay()
        self.overlay.calibrated.connect(self.on_calibrated)
        self.overlay.show()
        self.overlay.raise_()
        self.overlay.activateWindow()

    def on_calibrated(self, x1, y1, x2, y2):
        self.lbl_coords.setText(f"P1 (Vortex): ({x1}, {y1})\nP2 (Navegador): ({x2}, {y2})")
        self.add_log("INFO", f"Novos pontos calibrados salvas: P1=({x1}, {y1}), P2=({x2}, {y2})")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            config = load_config()
            self.worker.update_config(config)
            self.add_log("INFO", "Configurações atualizadas!")

    def reset_counter(self):
        self.worker.download_count = 0
        self.worker.ad_closed_count = 0
        self.update_count(0)
        self.update_ad_count(0)
        self.add_log("INFO", "Contadores de downloads e anúncios zerados.")

    def close_app(self):
        self.worker.set_running(False)
        self.worker.requestInterruption()
        self.worker.wait()
        self.close()
        sys.exit(0)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.update_exclude_rect()
