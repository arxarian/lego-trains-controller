import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/switch left.png"

    rotationData: [
        RotationData { objectName: "start"; dir: Globals.dir.start;
            angle: 0; point: Qt.point(0, 0); visible: true; next: 3 },
        RotationData { objectName: "start_flipped"; dir: Globals.dir.start;
            angle: 0; point: Qt.point(319, 0); visible: true; next: 2 },
        RotationData { objectName: "end_curved"; dir: Globals.dir.end;
            angle: 1; point: Qt.point(533, 1384); visible: true; next: 4 },
        RotationData { objectName: "end_curved_flipped"; dir: Globals.dir.end;
            angle: 1; point: Qt.point(829, 1261); visible: true; next: 5 },
        RotationData { objectName: "end_straight"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(0, 1279); visible: true; next: 1 },
        RotationData { objectName: "end_straight_flipped"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(319, 1279); visible: true; next: 0 }
    ]
}
