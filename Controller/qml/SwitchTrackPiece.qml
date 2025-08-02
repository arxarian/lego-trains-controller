import QtQuick
import TrainView

TrackPiece {
    id: root

    source: "qrc:/switch left.png"
    trackType: Globals.rail.switchRail

    rotationData: [
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(root.width, root.height); visible: true},
        RotationData { objectName: "up_straight"; dir: Globals.dir.up;
            angle: 1; point: Qt.point(295, 0); visible: true},
        RotationData { objectName: "up_curved"; dir: Globals.dir.up;
            angle: 0; point: Qt.point(root.width, 103); visible: true}
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
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: parent.width * 0.39
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(parent.index)
                root.rotationData[parent.index].visible = false
            }
        }
    }

    Rectangle {
        property int index: 1

        visible: rotationData[index].visible
        x: -25
        transformOrigin: Item.TopRight
        rotation: -22.5
        width: parent.width * 0.39
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(parent.index)
                root.rotationData[parent.index].visible = false
            }
        }
    }

    Rectangle {
        property int index: 2

        visible: rotationData[index].visible
        anchors.right: parent.right
        y: rotationData[index].point.y
        width: parent.width * 0.385
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(parent.index)
                root.rotationData[parent.index].visible = false
            }
        }
    }
}
