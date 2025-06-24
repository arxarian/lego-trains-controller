import QtQuick
import TrainsView

Image {
    id: root

    signal add(int index)

    property int trackType: -1

    property real originX: 0
    property real originY: 0
    property real angle: 0

    readonly property bool selected: Globals.selectedTrack === root

    required property list<RotationData> rotationData

    transform: Rotation { origin.x: root.originX; origin.y: root.originY; angle: root.angle}
    z: Globals.selectedTrack === root ? 10 : 0

    Component.onCompleted: Globals.selectedTrack = root

    Rectangle {
        anchors.fill: parent
        visible: Globals.trackFrameVisible
        color: "transparent"
        border.width: 4
    }

    Rectangle {
        id: selectedMarker

        anchors.fill: parent
        anchors.margins: -radius / 2
        radius: 40
        z: 10
        visible: root.selected
        color: "transparent"
        border.width: 20
        border.color: "gold"
    }

    Shortcut {
        enabled: root.selected
        sequences: ["R"]
        onActivated: console.log("R pressed")
    }

    MouseArea {
        anchors.fill: parent
        onClicked: Globals.selectedTrack = (root.selected ? null : root)
    }
}
