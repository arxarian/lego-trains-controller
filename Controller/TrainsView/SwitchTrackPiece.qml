import QtQuick

TrackPiece {
    id: root

    source: "qrc:/switch left.png"

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
        visible: root.topLeftVisible
        x: -18
        transformOrigin: Item.TopRight
        rotation: -22.5
        width: parent.width * 0.39
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add({angle: 1, offsetX: 226, offsetY: 0, rotationOrigin: Item.BottomRight})
                root.topLeftVisible = false
            }
        }
    }

    Rectangle {
        z: 1
        x: parent.width - width / 2
        y: 55 - height / 2
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
        visible: root.topRightVisible
        anchors.right: parent.right
        y: 55
        width: parent.width * 0.385
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add({angle: 0, offsetX: root.width, offsetY: 55, rotationOrigin: Item.BottomRight})
                root.topRightVisible = false
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
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: parent.width * 0.39
        height: 50

        color: "#55FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add({angle: -1, offsetX: root.width, offsetY: parent.height, rotationOrigin: Item.BottomRight})
                root.bottomVisible = false
            }
        }
    }
}
