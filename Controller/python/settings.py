# This Python file uses the following encoding: utf-8

from PySide6.QtCore import QObject, Signal, Property

DEFAULT_ZOOM = 0.3

class Settings(QObject):
    def __init__(self, canvas_x: float=0, canvas_y: float=0, canvas_zoom: float=DEFAULT_ZOOM, parent=None):
        super().__init__(parent)
        self._canvas_x = canvas_x
        self._canvas_y = canvas_y
        self._canvas_zoom = canvas_zoom

    def save_data(self):
        return {"canvas_x": self._canvas_x, "canvas_y": self._canvas_y,
            "canvas_zoom": round(self._canvas_zoom, 2)}

    def load_data(data, parent):
        return Settings(canvas_x=data.get("canvas_x", 0), canvas_y=data.get("canvas_y", 0),
            canvas_zoom=data.get("canvas_zoom", DEFAULT_ZOOM), parent=parent)

    def canvas_x(self):
        return self._canvas_x

    def set_canvas_x(self, value):
        self._canvas_x = value
        self.canvas_x_changed.emit()

    canvas_x_changed = Signal()
    canvas_x = Property(float, canvas_x, set_canvas_x, notify=canvas_x_changed)

    def canvas_y(self):
        return self._canvas_y

    def set_canvas_y(self, value):
        self._canvas_y = value
        self.canvas_y_changed.emit()

    canvas_y_changed = Signal()
    canvas_y = Property(float, canvas_y, set_canvas_y, notify=canvas_y_changed)

    def canvas_zoom(self):
        return self._canvas_zoom

    def set_canvas_zoom(self, value):
        self._canvas_zoom = value
        self.canvas_zoom_changed.emit()

    canvas_zoom_changed = Signal()
    canvas_zoom = Property(float, canvas_zoom, set_canvas_zoom, notify=canvas_zoom_changed)
