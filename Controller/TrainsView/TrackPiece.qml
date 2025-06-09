import QtQuick

Image {
    id: root

    // TODO is offset used?
    signal add(var tranformation)  //trans: int angle, int dir, real offsetX, real offsetY, int rotationOrigin

    property bool topVisible: true
    property bool bottomVisible: true
    property bool topLeftVisible: true
    property bool topRightVisible: true

    property int trackType: -1
    property real topOffsetX: 0
    property real bottomOffsetX: 0

    opacity: 0.8

    // Rectangle {
    //     anchors.fill: parent
    //     color: "transparent"
    //     border.width: 4
    // }
}
