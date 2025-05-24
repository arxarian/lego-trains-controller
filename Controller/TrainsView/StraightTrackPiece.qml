import QtQuick

TrackPiece {
    id: root

    source: "qrc:/straight.png"

    Rectangle {
        visible: root.topVisible
        width: parent.width
        height: 50
        
        color: "#55FF00FF"
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add({dir: 1})
                root.topVisible = false
            }
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
                root.add({dir: -1})
                root.bottomVisible = false
            }
        }
    }
}
