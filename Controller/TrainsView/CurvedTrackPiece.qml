import QtQuick

TrackPiece {
    id: root

    source: "qrc:/curved.png"
    trackType: 1

    topOffsetX: 104
    bottomOffsetX: 89

    Rectangle {
        z: 1
        x: 226 - width / 2
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
        x: -19
        transformOrigin: Item.TopRight
        rotation: -22.5
        width: parent.width * 0.74
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add({angle: 1, dir: 1, offsetX: 226, offsetY: 0})
                root.topVisible = false
            }
        }
    }

    Rectangle {
        z: 1
        x: parent.width - width / 2
        // x: 87 - width / 2
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
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: parent.width * 0.74
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add({angle: 0, dir: -1, offsetX: root.width, offsetY: parent.height})
                root.bottomVisible = false
            }
        }
    }
}
