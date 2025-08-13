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
            angle: 0; point: Qt.point(0, root.height); visible: true }

    ]

    Repeater {
        model: root.rotationData.length
        delegate: RotationPointMarker {
            x: rotationData[index].point.x - width / 2
            y: rotationData[index].point.y - height / 2
        }
    }

    Repeater {
        model: root.rotationData.length
        delegate: Rectangle {

            property RotationData config: rotationData[index]

            visible: config ? config.visible : false
            y: config ? config.point.y - (config.dir === Globals.dir.up ? 0 : height) : 0
            width: parent.width
            height: 50

            color: "#55FF00FF"

            MouseArea {
                anchors.fill: parent
                onClicked: {
                    root.add(index)
                    config.visible = false
                }
            }
        }
    }
}
