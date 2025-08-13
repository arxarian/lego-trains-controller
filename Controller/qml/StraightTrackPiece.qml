import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/straight.png"
    trackType: Rail.Straight

    rotationData: [
        RotationData { objectName: "up"; dir: Globals.dir.up;
            angle: 0; point: Qt.point(0, 0); visible: true },
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(0, 640); visible: true }

    ]
}
