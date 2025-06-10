import QtQuick
import TrainsView

TrackPiece {
    id: root

    source: "qrc:/straight.png"
    trackType: Globals.rail.straight

    rotationData: [
        RotationData { objectName: "up"; dir: Globals.dir.up;
            angle: 0; point: Qt.point(root.width, 0) },
        RotationData { objectName: "down"; dir: Globals.dir.down;
            angle: 0; point: Qt.point(root.width, root.height) }
    ]

    Rectangle {
        z: 1
        x: parent.width - width / 2
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
        width: parent.width
        height: 50
        
        color: "#55FF00FF"
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[0])
                // root.add({angle: 0, dir: Globals.dir.up, offsetX: root.width, offsetY: 0, rotationOrigin: Item.BottomRight})
                root.topVisible = false
            }
        }
    }

    Rectangle {
        z: 1
        x: parent.width - width / 2
        y: parent.height - height / 2
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
        visible: root.bottomVisible
        anchors.bottom: parent.bottom
        width: parent.width
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add(rotationData[1])
                // root.add({angle: 0, dir: Globals.dir.down, offsetX: root.width, offsetY: root.height, rotationOrigin: Item.TopRight})
                root.bottomVisible = false
            }
        }
    }
}
