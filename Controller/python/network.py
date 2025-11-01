from __future__ import annotations

from PySide6.QtCore import QObject, Slot

class Network(QObject):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    @Slot()
    def generate(self):
        print("Network: not implemented")
