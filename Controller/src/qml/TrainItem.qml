import QtQuick

Rectangle {
    id: root

    property Train trainData
    property real size: 300

    x: trainData.position.x - root.size / 2
    y: trainData.position.y - root.size / 2

    height: root.size
    width: root.size

    opacity: 0.8
    radius: height / 2
    color: "gold"
}
