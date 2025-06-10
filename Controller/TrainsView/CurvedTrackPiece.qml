import QtQuick
import TrainsView

TrackPiece {
    id: root

    source: "qrc:/curved.png"
    trackType: Globals.rail.curved

    rotationData: [
        RotationData { objectName: "up"; dir: Globals.dir.up;
            angle: 1; point: Qt.point(296, 0) },
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(root.width, root.height) }
    ]

    Rectangle {
        z: 1
        x: rotationData[0].point.x - width / 2
        y: - height / 2
        width: 20
        height: 20
        radius: width
        opacity: 0.8
        color: "gold"

        Rectangle {
            anchors.centerIn: parent
            width: 2
            height: 2
            color: "black"
        }
    }

    Rectangle {
        visible: root.topVisible
        x: -25
        transformOrigin: Item.TopRight
        rotation: -22.5
        width: parent.width * 0.75
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[0])
                root.topVisible = false
            }
        }
    }

    Rectangle {
        z: 1
        x: rotationData[1].point.x - width / 2
        y: rotationData[1].point.y - height / 2
        width: 20
        height: 20
        radius: width
        opacity: 0.8
        color: "red"

        Rectangle {
            anchors.centerIn: parent
            width: 2
            height: 2
            color: "black"
        }
    }

    Rectangle {
        visible: root.bottomVisible
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: parent.width * 0.75
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[1])
                root.bottomVisible = false
            }
        }
    }
}
