import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/switch left.png"

    rotationData: [
        RotationData { objectName: "up_curved"; dir: Globals.dir.up;
            angle: 1; point: Qt.point(0, 122); visible: true},
        RotationData { objectName: "up_straight"; dir: Globals.dir.up;
            angle: 0; point: Qt.point(509, 103); visible: true},
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(509, 1384); visible: true}
    ]
}
