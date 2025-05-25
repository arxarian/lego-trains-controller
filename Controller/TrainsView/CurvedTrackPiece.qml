import QtQuick

TrackPiece {
    id: root

    source: "qrc:/curved.png"

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
                root.add({angle: 1, offsetX: 226, offsetY: 0})
                root.topVisible = false
            }
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
                root.add({angle: -1, offsetX: root.width, offsetY: parent.height})
                root.bottomVisible = false
            }
        }
    }
}
