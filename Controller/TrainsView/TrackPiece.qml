import QtQuick

Image {
    id: root

    signal add(var tranformation)  //trans: int angle, int dir, real offsetX, real offsetY, int rotationOrigin

    property bool topVisible: true
    property bool bottomVisible: true
    property bool topLeftVisible: true
    property bool topRightVisible: true

}
