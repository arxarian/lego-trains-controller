import QtQuick

Item {
    id: root

    property real scaleFactor: 0.05
    property real minimalScale: 0.05
    property real maximalScale: 1

    MouseArea {
        id: mouseArea

        property real offsetX: 0
        property real offsetY: 0
        property real startX: 0
        property real startY: 0

        anchors.fill: parent
        onPressed: (mouse) => {
            mouseArea.startX = area.x
            mouseArea.startY = area.y
            mouseArea.offsetX = mouse.x
            mouseArea.offsetY = mouse.y
        }
        onPositionChanged: (mouse) => {
            area.x = mouse.x - mouseArea.offsetX + mouseArea.startX
            area.y = mouse.y - mouseArea.offsetY + mouseArea.startY
        }
    }

    WheelHandler {
        id: wheel
        onWheel: (event) => {
            if (event.angleDelta.y > 0) {
                area.scale = Math.min(maximalScale, area.scale + scaleFactor)
            } else {
                area.scale = Math.max(minimalScale, area.scale - scaleFactor)
            }
        }
    }

    function createSpriteObjects(sibling) {
        var component = Qt.createComponent("TrackPiece.qml");
        var sprite = component.createObject(area, {x: 0, y: 0});

        sprite.source = "qrc:/straight.png"
        sprite["add"].connect (function () {
            createSpriteObjects(sprite)
        })

        if (sibling) {
            sprite.x = sibling.x - sibling.width
        }
    }

    Component.onCompleted: root.createSpriteObjects()

    Item {
        id: area
        height: parent.height
        width: parent.width
        scale: 0.3
    }
}
