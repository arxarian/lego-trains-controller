import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/curved.png"

    rotationData: [
        RotationData { objectName: "start"; dir: Globals.dir.start;
            angle: 1; point: Qt.point(0, 122); visible: true; flipped: 3},
        RotationData { objectName: "end_flipped"; dir: Globals.dir.start;
            angle: 1; point: Qt.point(295, 0); visible: true; flipped: 2 },
        RotationData { objectName: "end"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(107, 658); visible: true; flipped: 1 },
        RotationData { objectName: "start_flipped"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(427, 658); visible: true; flipped: 0 }
    ]
}
