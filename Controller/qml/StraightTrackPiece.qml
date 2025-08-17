import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/straight.png"

    rotationData: [
        RotationData { objectName: "start"; dir: Globals.dir.start;
            angle: 0; point: Qt.point(0, 0); visible: true; flipped: 3 },
        RotationData { objectName: "end_flipped"; dir: Globals.dir.start;
            angle: 0; point: Qt.point(320, 0); visible: true; flipped: 2 },
        RotationData { objectName: "end"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(0, 640); visible: true; flipped: 1 },
        RotationData { objectName: "start_flipped"; dir: Globals.dir.end;
            angle: 0; point: Qt.point(320, 640); visible: true; flipped: 0 }
    ]
}
