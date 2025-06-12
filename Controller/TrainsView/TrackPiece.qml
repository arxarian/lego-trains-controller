import QtQuick
import TrainsView

Image {
    id: root

    // TODO is offset used?
    signal add(int index)

    property int trackType: -1

    property real originX: 0
    property real originY: 0
    property real angle: 0

    property list<RotationData> rotationData    // TODO - required?

    opacity: 0.8

    transform: Rotation { origin.x: root.originX; origin.y: root.originY; angle: root.angle}

    Rectangle {
        anchors.fill: parent
        visible: Globals.trackFrameVisible
        color: "transparent"
        border.width: 4
    }
}
