import sys

from PySide6.QtWidgets import QApplication

from terdash.app import TerDashWindow


def main():
    app = QApplication(sys.argv)
    window = TerDashWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
