import sys
from PySide6.QtWidgets import QApplication
from pet_app.main_window import DesktopPetWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = DesktopPetWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
