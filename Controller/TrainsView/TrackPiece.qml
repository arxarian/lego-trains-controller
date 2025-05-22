import QtQuick

Image {
    id: root

    signal add()

    Rectangle {
        anchors.left: parent.left
        width: 20
        height: parent.height
        
        color: "#88FF00FF"
        
        MouseArea {
            anchors.fill: parent
            onClicked: {
                root.add()
                parent.visible = false
            }
        }
    }
}
