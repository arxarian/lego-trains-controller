import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/switch left.png"

    rotationData: [
        RotationData { objectName: "upper_curved"; dir: Globals.dir.end;
            angle: 1; point: Qt.point(0, 122); visible: true},
        RotationData { objectName: "upper_straight"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(509, 103); visible: true},
        RotationData { objectName: "bottom"; dir: Globals.dir.start;
            angle: 0; point: Qt.point(509, 1384); visible: true}
    ]
}
