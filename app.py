from PySide6.QtWidgets import QApplication
import window
import sys

qap = QApplication(sys.argv)
app = window.FetchLiteWindow()
app.show()
sys.exit(qap.exec())
