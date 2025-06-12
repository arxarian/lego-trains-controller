import QtQuick
import TrainsView

TrackPiece {
    id: root

    source: "qrc:/curved.png"
    trackType: Globals.rail.curved

    rotationData: [
        RotationData { objectName: "up"; dir: Globals.dir.up;
            angle: 1; point: Qt.point(296, 0); visible: true },
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(root.width, root.height); visible: true }
    ]

    Repeater {
        model: root.rotationData.length
        delegate: RotationPointMarker {
            x: rotationData[index].point.x - width / 2
            y: rotationData[index].point.y - height / 2
        }
    }

    Rectangle {
        visible: rotationData[0].visible
        x: -25
        transformOrigin: Item.TopRight
        rotation: -22.5
        width: parent.width * 0.75
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(0)
                rotationData[0].visible = false
            }
        }
    }

    Rectangle {
        visible: rotationData[1].visible
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: parent.width * 0.75
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(1)
                rotationData[1].visible = false
            }
        }
    }
}
