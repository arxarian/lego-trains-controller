import QtQuick

TrackPiece {
    id: root

    source: "qrc:/curved.png"
    trackType: Globals.rail.curved

    topOffsetX: 296
    topRotation: 1
    bottomOffsetX: width

    Rectangle {
        z: 1
        x: root.topOffsetX - width / 2
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
                root.add({angle: 1, dir: Globals.dir.up, offsetX: root.topOffsetX, offsetY: 0})
                root.topVisible = false
            }
        }
    }

    Rectangle {
        z: 1
        x: root.bottomOffsetX - width / 2
        y: parent.height - height / 2
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
                root.add({angle: 0, dir: Globals.dir.down, offsetX: root.bottomOffsetX, offsetY: root.height})
                root.bottomVisible = false
            }
        }
    }
}
