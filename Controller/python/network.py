from __future__ import annotations

from PySide6.QtCore import QObject

class Network(QObject):

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
