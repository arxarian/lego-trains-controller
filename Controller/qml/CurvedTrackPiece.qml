import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/curved.png"

    rotationData: [
        RotationData { objectName: "up"; dir: Globals.dir.up;
            angle: 1; point: Qt.point(0, 122); visible: true },
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(107, 658); visible: true }
    ]
}
