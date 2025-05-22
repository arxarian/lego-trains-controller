import QtQuick

MouseArea {
    id: root

    property real scaleFactor: 0.05
    property real minimalScale: 0.05

    onWheel: {
        if (wheel.angleDelta.y > 0) {
            area.scale += scaleFactor
        } else {
            area.scale = Math.max(minimalScale, area.scale - scaleFactor)
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
            console.log("heyy")
            sprite.x = sibling.x - sibling.width
        }
    }

    Component.onCompleted: root.createSpriteObjects()

    Item {
        id: area
        anchors.fill: parent
        scale: 0.3
    }
}
