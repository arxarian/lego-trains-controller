import QtQuick

Image {
    id: root

    signal add(var dir)

    property bool leftVisible: true
    property bool rightVisible: true

    source: "qrc:/straight.png"

    Rectangle {
        visible: root.leftVisible
        anchors.left: parent.left
        width: 20
        height: parent.height
        
        color: "#88FF00FF"
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add("left")
                root.leftVisible = false
            }
        }
    }

    Rectangle {
        visible: root.rightVisible
        anchors.left: parent.right
        width: 20
        height: parent.height

        color: "#88FF00FF"

        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add("right")
                root.rightVisible = false
            }
        }
    }
}
