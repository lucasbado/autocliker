from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from pynput import mouse
from autoclicker_core import load_config, save_config

class GlobalMouseListener(QThread):
    click_captured = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.listener = None

    def run(self):
        def on_click(x, y, button, pressed):
            if button == mouse.Button.left and not pressed:
                # Dispara sinal no clique liberado (mouse release)
                self.click_captured.emit(int(x), int(y))
                return False  # Para o listener apos um clique

        self.listener = mouse.Listener(on_click=on_click)
        self.listener.start()
        self.listener.join()

    def stop(self):
        if self.listener:
            self.listener.stop()


class CalibrationOverlay(QWidget):
    calibrated = pyqtSignal(int, int, int, int)  # (x1, y1, x2, y2)

    def __init__(self):
        super().__init__()
        self.step = 1
        self.p1_x = 0
        self.p1_y = 0
        self.listener_thread = None

        # Janela pequena de instruções no topo do monitor (não bloqueia os cliques do mouse)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedWidth(520)
        self.setFixedHeight(180)

        # Posiciona no topo central da tela
        screen = self.screen()
        if screen:
            geo = screen.geometry()
            self.move((geo.width() - 520) // 2, 40)
        else:
            self.move(300, 40)

        layout = QVBoxLayout(self)

        self.label = QLabel(
            "📍 PASSO 1/2 DE CALIBRAÇÃO 📍\n\n"
            "Clique em QUALQUER LUGAR da tela onde fica a Notificação / Vortex.\n"
            "(O clique passará normalmente para o programa embaixo!)"
        )
        self.label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.label.setStyleSheet(
            "color: white; "
            "background-color: rgba(18, 24, 36, 245); "
            "padding: 16px; "
            "border-radius: 12px; "
            "border: 2px solid #00E676;"
        )
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.btn_cancel = QPushButton("Cancelar Calibração (ESC)")
        self.btn_cancel.setFont(QFont("Segoe UI", 9))
        self.btn_cancel.setStyleSheet(
            "background-color: #C62828; color: white; padding: 6px 12px; border-radius: 6px;"
        )
        self.btn_cancel.clicked.connect(self.close_calibration)
        layout.addWidget(self.btn_cancel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.start_click_listener()

        # Exibe visivelmente a janela de calibração
        self.show()
        self.raise_()
        self.activateWindow()

    def start_click_listener(self):
        if self.listener_thread:
            self.listener_thread.stop()

        self.listener_thread = GlobalMouseListener()
        self.listener_thread.click_captured.connect(self.on_mouse_clicked)
        self.listener_thread.start()

    def on_mouse_clicked(self, x, y):
        if self.step == 1:
            self.p1_x = x
            self.p1_y = y
            self.step = 2

            self.label.setText(
                f"✅ Ponto 1 Salvo: ({x}, {y})\n\n"
                "📍 PASSO 2/2 DE CALIBRAÇÃO 📍\n"
                "Agora clique no botão 'Slow Download' no seu Navegador."
            )
            self.label.setStyleSheet(
                "color: white; "
                "background-color: rgba(18, 24, 36, 245); "
                "padding: 16px; "
                "border-radius: 12px; "
                "border: 2px solid #1E88E5;"
            )
            # Inicia escuta para o Ponto 2
            self.start_click_listener()

        elif self.step == 2:
            p2_x, p2_y = x, y

            config = load_config()
            config["step1_x"] = self.p1_x
            config["step1_y"] = self.p1_y
            config["step2_x"] = p2_x
            config["step2_y"] = p2_y
            save_config(config)

            self.calibrated.emit(self.p1_x, self.p1_y, p2_x, p2_y)
            self.close_calibration()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close_calibration()

    def close_calibration(self):
        if self.listener_thread:
            self.listener_thread.stop()
            self.listener_thread = None
        self.close()
