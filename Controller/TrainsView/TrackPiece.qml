import QtQuick
import TrainsView

Image {
    id: root

    // TODO is offset used?
    signal add(var tranformation)  //trans: int angle, int dir, real offsetX, real offsetY, int rotationOrigin

    property bool topVisible: true
    property bool bottomVisible: true
    property bool topLeftVisible: true
    property bool topRightVisible: true

    property int trackType: -1

    property real originX: 0
    property real originY: 0
    property real angle: 0

    property list<RotationData> rotationData    // TODO - required?

    opacity: 0.8

    transform: Rotation { origin.x: root.originX; origin.y: root.originY; angle: root.angle}

    Rectangle {
        anchors.fill: parent
        color: "transparent"
        border.width: 4
    }
}
