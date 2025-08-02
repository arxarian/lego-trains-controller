import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/straight.png"
    trackType: Rail.Straight

    rotationData: [
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(root.width, root.height); visible: true },
        RotationData { objectName: "up"; dir: Globals.dir.up;
            angle: 0; point: Qt.point(root.width, 0); visible: true }
    ]

    Repeater {
        model: root.rotationData.length
        delegate: RotationPointMarker {
            x: rotationData[index].point.x - width / 2
            y: rotationData[index].point.y - height / 2
        }
    }

    Rectangle {
        property int index: 0

        visible: rotationData[index].visible
        width: parent.width
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(parent.index)
                rotationData[parent.index].visible = false
            }
        }
    }

    Rectangle {
        property int index: 1

        visible: rotationData[index].visible
        anchors.bottom: parent.bottom
        width: parent.width
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(parent.index)
                rotationData[parent.index].visible = false
            }
        }
    }
}
