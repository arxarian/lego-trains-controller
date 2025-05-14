from __future__ import annotations

from PySide6.QtCore import QObject, Slot

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

class Devices(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)

    @Slot(str)
    def connect_to(self, hub_name):
        print("Wanna connect to ", hub_name)
