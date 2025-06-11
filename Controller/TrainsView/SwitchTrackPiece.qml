import QtQuick
import TrainsView

TrackPiece {
    id: root

    source: "qrc:/switch left.png"
    trackType: Globals.rail.switchRail

    rotationData: [
        RotationData { objectName: "up_straight"; dir: Globals.dir.up;
            angle: 1; point: Qt.point(295, 0) },
        RotationData { objectName: "up_curved"; dir: Globals.dir.up;
            angle: 0; point: Qt.point(root.width, 103) },
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(root.width, root.height) }
    ]

    RotationPointMarker {
        x: rotationData[0].point.x - width / 2
        y: rotationData[0].point.y - height / 2
    }

    Rectangle {
        visible: root.topLeftVisible
        x: -25
        transformOrigin: Item.TopRight
        rotation: -22.5
        width: parent.width * 0.39
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[0])
                root.topLeftVisible = false
            }
        }
    }

    RotationPointMarker {
        x: rotationData[1].point.x - width / 2
        y: rotationData[1].point.y - height / 2
    }

    Rectangle {
        visible: root.topRightVisible
        anchors.right: parent.right
        y: rotationData[1].point.y
        width: parent.width * 0.385
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[1])
                root.topRightVisible = false
            }
        }
    }

    RotationPointMarker {
        x: rotationData[2].point.x - width / 2
        y: rotationData[2].point.y - height / 2
    }

    Rectangle {
        visible: root.bottomVisible
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: parent.width * 0.39
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[2])
                root.bottomVisible = false
            }
        }
    }
}
