import sys
from PyQt6.QtWidgets import QApplication
from floating_widget import FloatingWidget

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)

    widget = FloatingWidget()
    
    # Posiciona a janela flutuante no canto superior direito do monitor principal
    screen = app.primaryScreen()
    if screen:
        screen_geo = screen.geometry()
        widget.move(screen_geo.width() - 340, 120)
    else:
        widget.move(100, 100)

    widget.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
